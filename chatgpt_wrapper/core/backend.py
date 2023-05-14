from abc import ABC, abstractmethod
from typing import Any

from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from chatgpt_wrapper.core.logger import logger

from chatgpt_wrapper.core.config import Config
from chatgpt_wrapper.core import util

class VerboseStreamingStdOutCallbackHandler(StreamingStdOutCallbackHandler):
    @property
    def always_verbose(self) -> bool:
        """Whether to call verbose callbacks even if verbose is False."""
        return True

def make_interrupt_streaming_callback_handler(backend):
    class InterruptStreamingCallbackHandler(VerboseStreamingStdOutCallbackHandler):
        def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
            if not backend.streaming:
                util.print_status_message(False, "\n\nWARNING:\nStream interruption on the API backend is not currently working properly, and may not properly store information on an interrupted stream.\nIf you'd like to help fix this error, see https://github.com/mmabrouk/chatgpt-wrapper/issues/274")
                message = "Request to interrupt streaming"
                backend.log.info(message)
                raise EOFError(message)
    return InterruptStreamingCallbackHandler()

class Backend(ABC):
    """
    Base class/interface for all backends.
    """

    def __init__(self, config=None):
        self.name = self.get_backend_name()
        self.config = config or Config()
        # logger = ThreadSafeLogger(self.__class__.__name__)
        self.parent_message_id = None
        self.conversation_id = None
        self.conversation_title_set = None
        self.message_clipboard = None
        self.streaming = False
        self.interrupt_streaming_callback_handler = make_interrupt_streaming_callback_handler(self)
        self.set_available_models()
        self.set_active_model(self.config.get('chat.model'))

    def set_llm_class(self, klass):
        self.llm_class = klass

    def get_default_llm_args(self):
        return {
            'temperature': 0,
            'model_name': self.model,
        }

    def streaming_args(self, interrupt_handler=False):
        calback_handlers = [
            VerboseStreamingStdOutCallbackHandler(),
        ]
        if interrupt_handler:
            calback_handlers.append(self.interrupt_streaming_callback_handler)
        args = {
            'streaming': True,
            'callback_manager': CallbackManager(calback_handlers),
        }
        return args

    def make_llm(self, args={}):
        final_args = self.get_default_llm_args()
        final_args.update(args)
        llm = self.llm_class(**final_args)
        return llm

    def set_active_model(self, model=None):
        if model is None:
            self.model = None
        else:
            self.model = self.available_models[model]

    def new_conversation(self):
        self.parent_message_id = None
        self.conversation_id = None
        self.conversation_title_set = None
        self.message_clipboard = None

    def terminate_stream(self, _signal, _frame):
        logger.info("Received signal to terminate stream")
        if self.streaming:
            self.streaming = False

    def get_runtime_config(self):
        return ""

    @abstractmethod
    def get_backend_name(self):
        pass

    @abstractmethod
    def set_available_models(self):
        pass

    @abstractmethod
    def ask_stream(self, prompt: str):
        pass

    @abstractmethod
    def ask(self, message: str):
        pass
