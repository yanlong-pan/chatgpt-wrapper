import os
import threading
from typing import List
import openai
import tiktoken

from langchain.chat_models.openai import ChatOpenAI, _convert_dict_to_message
from chatgpt_wrapper.backends.openai.character import CharacterManager
from chatgpt_wrapper.backends.openai.orm import Conversation

from chatgpt_wrapper.core.backend import Backend
import chatgpt_wrapper.core.constants as constants
import chatgpt_wrapper.core.util as util
from chatgpt_wrapper.backends.openai.user import UserManager
from chatgpt_wrapper.backends.openai.conversation import ConversationManager
from chatgpt_wrapper.backends.openai.message import MessageManager
from chatgpt_wrapper.core.logger import logger
class OpenAIAPI(Backend):
    def __init__(self, config=None):
        super().__init__(config)
        self._configure_access_info()
        self.um = UserManager()
        self.cm = ConversationManager()
        self.mm = MessageManager()
        self.chm = CharacterManager()
        self.conversation = None
        self.conversation_tokens = 0
        self.set_llm_class(ChatOpenAI)
        self.set_model_system_message()
        self.set_model_temperature(self.config.get('chat.model_customizations.temperature'))
        self.set_model_top_p(self.config.get('chat.model_customizations.top_p'))
        self.set_model_presence_penalty(self.config.get('chat.model_customizations.presence_penalty'))
        self.set_model_frequency_penalty(self.config.get('chat.model_customizations.frequency_penalty'))
        self.set_model_max_submission_tokens(self.config.get('chat.model_customizations.max_submission_tokens'))

    def _configure_access_info(self):
        self.openai = openai
        profile_prefix = f"PROFILE_{self.config.profile.upper()}"
        self.openai.organization = os.getenv(f"{profile_prefix}_OPENAI_ORG_ID")
        if not self.openai.organization:
            self.openai.organization = os.getenv("OPENAI_ORG_ID")
        self.openai.api_key = os.getenv(f"{profile_prefix}_OPENAI_API_KEY")
        if not self.openai.api_key:
            self.openai.api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai.api_key:
            raise ValueError(f"{profile_prefix}_OPENAI_API_KEY or OPENAI_API_KEY environment variable must be set")

    def _handle_response(self, success, obj, message):
        if not success:
            logger.error(message)
        return success, obj, message

    def get_token_encoding(self, model="gpt-3.5-turbo"):
        if model not in self.available_models.values():
            raise NotImplementedError("Unsupported engine {self.engine}")
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            raise Exception(f"Unable to get token encoding for model {model}: {str(e)}")
        return encoding

    def get_num_tokens_from_messages(self, messages, encoding=None):
        if not encoding:
            encoding = self.get_token_encoding()
        """Returns the number of tokens used by a list of messages."""
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
        
    def switch_to_conversation(self, conversation, parent_message_id):
        self.parent_message_id = parent_message_id
        self.bind_conversation(conversation)
        tokens = self.get_conversation_token_count()
        self.conversation_tokens = tokens

    def get_conversation_token_count(self):
        success, old_messages, user_message = self.mm.get_messages(self.conversation_id)
        if not success:
            raise Exception(user_message)
        token_messages = self.prepare_prompt_messsage_context(old_messages)
        tokens = self.get_num_tokens_from_messages(token_messages)
        return tokens

    def extract_system_message(self, model_customizations):
        system_message = None
        if 'system_message' in model_customizations:
            system_message = model_customizations['system_message']
            del model_customizations['system_message']
            aliases = self.get_system_message_aliases()
            if system_message in aliases:
                system_message = aliases[system_message]
        return system_message, model_customizations

    def _extract_message_content(self, message):
        return message.content

    def get_backend_name(self):
        return "chatgpt-api"

    def set_available_models(self):
        self.available_models = constants.OPENAPI_CHAT_RENDER_MODELS

    def set_model_system_message(self, message=constants.SYSTEM_MESSAGE_DEFAULT):
        self.model_system_message = message

    def set_model_temperature(self, temperature=constants.OPENAPI_DEFAULT_TEMPERATURE):
        self.model_temperature = temperature

    def set_model_top_p(self, top_p=constants.OPENAPI_DEFAULT_TOP_P):
        self.model_top_p = top_p

    def set_model_presence_penalty(self, presence_penalty=constants.OPENAPI_DEFAULT_PRESENCE_PENALTY):
        self.model_presence_penalty = presence_penalty

    def set_model_frequency_penalty(self, frequency_penalty=constants.OPENAPI_DEFAULT_FREQUENCY_PENALTY):
        self.model_frequency_penalty = frequency_penalty

    def set_model_max_submission_tokens(self, max_submission_tokens=constants.OPENAPI_DEFAULT_MAX_SUBMISSION_TOKENS):
        self.model_max_submission_tokens = max_submission_tokens

    def get_runtime_config(self):
        output = """
* Model customizations:
  * Model: %s
  * Temperature: %s
  * top_p: %s
  * Presence penalty: %s
  * Frequency penalty: %s
  * Max submission tokens: %s
  * System message: %s
""" % (self.model, self.model_temperature, self.model_top_p, self.model_presence_penalty, self.model_frequency_penalty, self.model_max_submission_tokens, self.model_system_message)
        return output

    def get_system_message_aliases(self):
        aliases = self.config.get('chat.model_customizations.system_message')
        aliases['default'] = constants.SYSTEM_MESSAGE_DEFAULT
        return aliases

    def build_openai_message(self, role, content):
        message = {
            "role": role,
            "content": content,
        }
        return message

    def prepare_prompt_conversation_messages(self, prompt, target_id=None, system_message=None):
        old_messages = []
        new_messages = []
        success, old_messages, message = self.mm.get_messages(self.conversation_id, target_id=target_id)
        if not success:
            raise Exception(message)
        if len(old_messages) == 0:
            system_message = system_message or self.model_system_message
            new_messages.append(self.build_openai_message('system', system_message))
        new_messages.append(self.build_openai_message('user', prompt))
        return old_messages, new_messages

    def prepare_prompt_messsage_context(self, old_messages=[], new_messages=[]):
        messages = [self.build_openai_message(m.role, m.message) for m in old_messages]
        messages.extend(new_messages)
        return messages

    def _build_openai_chat_request(self, messages, temperature=None, top_p=None, presence_penalty=None, frequency_penalty=None, stream=False):
        temperature = self.model_temperature if temperature is None else temperature
        top_p = self.model_top_p if top_p is None else top_p
        presence_penalty = self.model_presence_penalty if presence_penalty is None else presence_penalty
        frequency_penalty = self.model_frequency_penalty if frequency_penalty is None else frequency_penalty
        logger.debug(f"PID:{os.getpid()} TID:{threading.current_thread().ident} obj_id:{id(self)} ChatCompletion.create with message count: {len(messages)}, model: {self.model}, temperature: {temperature}, top_p: {top_p}, presence_penalty: {presence_penalty}, frequency_penalty: {frequency_penalty}, stream: {stream})")
        args = {
            'model_name': self.model,
            'temperature': temperature,
            'top_p': top_p,
            'presence_penalty': presence_penalty,
            'frequency_penalty': frequency_penalty,
        }
        if stream:
            args.update(self.streaming_args(interrupt_handler=True))
        llm = self.make_llm(args)
        messages = [_convert_dict_to_message(m) for m in messages]
        return llm, messages

    def _call_openai_streaming(self, messages, temperature=None, top_p=None, presence_penalty=None, frequency_penalty=None):
        logger.debug(f"Initiated streaming request with message count: {len(messages)}")
        llm, messages = self._build_openai_chat_request(messages, temperature=temperature, top_p=top_p, presence_penalty=presence_penalty, frequency_penalty=frequency_penalty, stream=True)
        try:
            response = llm(messages)
        except ValueError as e:
            return False, messages, e
        return True, response, "Response received"

    def _call_openai_non_streaming(self, messages, temperature=None, top_p=None, presence_penalty=None, frequency_penalty=None):
        logger.debug(f"Initiated non-streaming request with message count: {len(messages)} {threading.current_thread().name}")
        llm, messages = self._build_openai_chat_request(messages, temperature=temperature, top_p=top_p, presence_penalty=presence_penalty, frequency_penalty=frequency_penalty)
        try:
            response = llm(messages)
        except ValueError as e:
            return False, messages, e
        return True, response, "Response received"

    def bind_conversation(self, conversation: Conversation):
        self.conversation = conversation
        self.conversation_id = conversation.id
    
    def new_conversation(self, user_id, character_id):
        super().new_conversation()
        self.conversation_tokens = 0
        success, conversation, message = self.cm.add_conversation(user_id, character_id, model=self.model)
        if success:    
            self.bind_conversation(conversation)
            return conversation
        else:
            raise Exception(message)
        
    def _strip_out_messages_over_max_tokens(self, messages, token_count, max_tokens):
        stripped_messages_count = 0
        while token_count > max_tokens and len(messages) > 1:
            message = messages.pop(0)
            token_count = self.get_num_tokens_from_messages(messages)
            logger.debug(f"Stripping message: {message['role']}, {message['content']} -- new token count: {token_count}")
            stripped_messages_count += 1
        token_count = self.get_num_tokens_from_messages(messages)
        if token_count > max_tokens:
            raise Exception(f"No messages to send, all messages have been stripped, still over max submission tokens: {max_tokens}")
        if stripped_messages_count > 0:
            max_tokens_exceeded_warning = f"Conversation exceeded max submission tokens ({max_tokens}), stripped out {stripped_messages_count} oldest messages before sending, sent {token_count} tokens instead"
            logger.warning(max_tokens_exceeded_warning)
            util.print_status_message(False, max_tokens_exceeded_warning)
        return messages

    def _prepare_ask_request(self, prompt, system_message=None):
        old_messages, new_messages = self.prepare_prompt_conversation_messages(prompt, self.parent_message_id, system_message=system_message)
        messages = self.prepare_prompt_messsage_context(old_messages, new_messages)
        tokens = self.get_num_tokens_from_messages(messages)
        self.conversation_tokens = tokens
        messages = self._strip_out_messages_over_max_tokens(messages, self.conversation_tokens, self.model_max_submission_tokens)
        logger.debug(messages)
        return new_messages, messages

    def _ask_request_post(self, new_messages: List[dict], response_message, title=None):
        try:
            if not response_message:
                return False, None, "Conversation not updated with new messages"
            logger.debug(new_messages)
            _, msgs, _ = self.mm.add_messages(
                self.conversation_id,
                [*new_messages, self.build_openai_message('assistant', response_message)]
            )
            logger.debug(msgs)
            
            self.parent_message_id = msgs[-1].id
        except Exception as e:
            return self._handle_response(False, None, f"Fail to add messages to conversation {str(e)}")
        # TODO: refine token count
        tokens = self.get_conversation_token_count()
        self.conversation_tokens = tokens
        return True, self.conversation, "Conversation updated with new messages"
    
    def ask_stream(self, prompt, title=None, model_customizations={}):
        system_message, model_customizations = self.extract_system_message(model_customizations)
        new_messages, messages = self._prepare_ask_request(prompt, system_message=system_message)
        # Streaming loop.
        self.streaming = True
        #    if not self.streaming:
        #        logger.info("Request to interrupt streaming")
        #        break
        logger.debug(f"Started streaming response at {util.current_datetime().isoformat()}")
        success, response_obj, user_message = self._call_openai_streaming(messages, **model_customizations)
        if success:
            logger.debug(f"Stopped streaming response at {util.current_datetime().isoformat()}")
            response_message = self._extract_message_content(response_obj)
            self.message_clipboard = response_message
            if not self.streaming:
                util.print_status_message(False, "Generation stopped")
            success, response_obj, user_message = self._ask_request_post(new_messages, response_message, title)
            if success:
                response_obj = response_message
        # End streaming loop.
        self.streaming = False
        return self._handle_response(success, response_obj, user_message)

    def ask(self, prompt, title=None, model_customizations={}):
        """
        Send a message to chatGPT and return the response.

        Args:
            message (str): The message to send.

        Returns:
            str: The response received from OpenAI.
        """
        system_message, model_customizations = self.extract_system_message(model_customizations)
        new_messages, messages = self._prepare_ask_request(prompt, system_message=system_message)
        success, response, user_message = self._call_openai_non_streaming(messages, **model_customizations)
        if success:
            response_message = self._extract_message_content(response)
            self.message_clipboard = response_message
            success, conversation, user_message = self._ask_request_post(new_messages, response_message, title)
            if success:
                return self._handle_response(success, response_message, user_message)
            return self._handle_response(success, conversation, user_message)
        return self._handle_response(success, response, user_message)
