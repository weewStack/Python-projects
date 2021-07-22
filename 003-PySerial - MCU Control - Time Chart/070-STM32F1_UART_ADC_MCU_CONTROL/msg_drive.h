#include "uart_drive.h"
#include "help_func.h"
#include "adc_drive.h"


void basic_msg(char uart, int val);
char get_port(char port);
char get_pin(char * str);
char pin_on_off(char * USART_msg, char uart);
char adc_on_off(char * USART_msg, char * gui_control);

