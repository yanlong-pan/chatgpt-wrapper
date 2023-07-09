from nb_log import get_logger

logger = get_logger(
    'app',
    log_level_int = 10,
    do_not_use_color_handler = True,
    log_path = 'logs',
    log_filename = 'test_nb_log.log',
    log_file_size = 200,
    log_file_handler_type = 1,
    formatter_template = 2
)

console_logger = get_logger(
    'console'
)