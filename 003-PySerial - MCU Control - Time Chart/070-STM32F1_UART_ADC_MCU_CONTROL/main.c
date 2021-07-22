// Adding msg_drive.h and commenting both help_func & uart_drive

#include "msg_drive.h"

//#include "adc_drive.h"
//#include "help_func.h"
//#include "uart_drive.h"



char num[10]; // String for Int conversion
int analog_rx = 0; // Variable to read the ADC value

char gui_control[1]={0}; // GUI Manager Gui 0: Controller sending the ADC data


/*
UART Manager
0- count
1- signal
2- Bridge
3- Terminator data load 1: Terminator / 0: Interrupt
4- terminator char 
5- time cst
6- time counter 

*/

unsigned short uart_2_mgr[7]={0,0,0,1,'\n',0,0};
char USART_2_msg[100];
/*
unsigned short uart_3_mgr[7]={0,0,0,1,'\n',0,0};
char USART_3_msg[100];
*/
int main(void)
{

	systick_init();// Initiate the delayms function
	UART_init(2,115200);// Initialize the UART Commnunication
	Digital_Output(PC,13); // Set up Port C Pin 13 as output Pin

while(1)
{
	if(uart_2_mgr[1])
	{
		uart_2_mgr[1]=0;
		pin_on_off(USART_2_msg, 2);
		adc_on_off(USART_2_msg,gui_control);
		str_empty(USART_2_msg);
	}
	if(gui_control[0])
	{
		if(adc_check(adc1, PA, 0))
		{
			analog_rx = adc_rx(adc1, PA, 0);
			basic_msg(2, analog_rx);
		}
	}
	
}
}
//UART interrupt to handle the reception incoming messages
void USART2_IRQHandler()
{

	UART_ISR(2,uart_2_mgr, USART_2_msg);
}
/*
void USART3_IRQHandler()
{
	UART_ISR(3,uart_3_mgr, USART_3_msg);
}
*/
