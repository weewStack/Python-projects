#include "msg_drive.h"

// Send basic UART message
void basic_msg(char uart, int val)
{
	char num[10];
	int2char(val,num);
	UART_SEND(uart,num);
	str_empty(num);
	UART_TX(2,'\n');
}

// Gets the Port number from UART msaage
char get_port(char port)
{
	if(port == 'A')
	{
		return PA;
	}
	else if(port == 'B')
	{
		return PB;
	}
	else if(port == 'C')
	{
		return PC;
	}
	return 0;
	
}

// Gets the Pin number from UART msaage
char get_pin(char * str)
{
	char num[2];
	char pin;
	
	num[0] = str[2];
	num[1] = str[3];
	pin = char2int(num);
	
	return pin;
}


char pin_on_off(char * USART_msg, char uart)
{
	char level;
	if((USART_msg[0] == '0') | (USART_msg[0] == '1'))
		{
			if(get_port(USART_msg[1]))
			{
				
				level = USART_msg[0] - 48;
				W_GP(get_port(USART_msg[1]),get_pin(USART_msg),level);
				return 1;
			}
		
		}
		return 0;
}

char adc_on_off(char * USART_msg,  char * gui_control)
{
	char adc;
	if(USART_msg[0] == 'A')
		{
			
				if(get_port(USART_msg[1]))
				{
					if(USART_msg[4] == '1')
					{
						adc = USART_msg[4]-48;
						adc_init(adc, get_port(USART_msg[1]), get_pin(USART_msg));
						
						DelayMs(30);
						gui_control[0] = 1;
						return 1;
						
					}
					else if(USART_msg[4] == '0')
					{
						
						adc = USART_msg[4]-48;
						DelayMs(30);
						gui_control[0] = 0;
						return 1;
					}
				}
				
			
		
		}
		return 0;
}
