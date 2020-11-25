/* server-select.c */
/*
U的那个操作方式是：nc -u 127.0.0.1 54709
T的那个操作方式是：netcat local host 8128
这个作业的感觉，暂时目前来说，写两个select。然后循环查看。

*/
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>

#include <sys/select.h>      /* <===== */

#define BUFFER_SIZE 1024
#define MAX_CLIENTS 100      /* <===== */
#define MAXBUFFER 1024
#define ADDRBUFFER 128
#define MAXTHREADS  100




int find_fd(char* ID, char** IDlist){

    int found = -1;
    for(int i=0;i<MAX_CLIENTS*2; i=i+2){

          if(strcmp(IDlist[i], ID)==0){
            found = i;

            break;
          }else{
            continue;
          }
    }

    if(found<0){
      return found;
    }else{
      int result = atoi(IDlist[found+1]);
      return result;

    }

}



char* find_ID(char* fd_number, char** IDlist){

    int found = -1;
    for(int i=1;i<MAX_CLIENTS*2; i=i+2){
      if(strcmp(IDlist[i], "empty\0")!=0){

      }
          if(strcmp(IDlist[i], fd_number)==0){

            found = i;

            break;
          }else{
            continue;
          }
    }

    if(found<0){

      return fd_number;
    }else{
      return IDlist[found-1] ;

    }

}







void cut_send(char* send, char*  ID,  int* number, char* message){
  int n = 0;
  int first = 0;
  int second = 0;

  char numberss[5];

  char copy[100]; 
  strcpy(copy, send);

  n=5;
  while(second==0){

    if(copy[n]==' '&&first==0){
      first =n;
    }
    n++;

    if(copy[n]=='\n'){
      second= n;
     }

  }

  strncpy(ID, send+5, first-5);
  ID[first-5]='\0';

  strncpy(numberss, send+first+1, second-first-1);
  numberss[second-first-1]='\0';

  *number= atoi(numberss);

  strncpy(message, send+second+1, strlen(send)-second-1);
  message[strlen(send)-second-1]='\0';

}




void cut_broadcast(char* send,  int* number, char* message){
  int n = 0;
  int first = 0;

  int third = 0;
  char numberss[5];

  char copy[100]; 
  strcpy(copy, send);



  n=8;
  while(n<strlen(copy)){

    if(copy[n]==' '&&first==0){
      first =n;
    }
    n++;
   if(copy[n]=='\n'){
      third =n;
     
    }




    if(third>0){
      break;
    }

  }



  strncpy(numberss, copy+first+1, third-first-1);
  numberss[third-first-1]='\0';
  // printf("numberss=%s, length = %ld\n", numberss, strlen(numberss));

  *number= atoi(numberss);
  // printf("number =%d\n", *number);


  strncpy(message, copy+third+1, *number);
  message[*number]='\0';
  // printf("message=%s, length = %ld\n", message, strlen(message));


}

void print_IDlist(char** IDlist){

  for(int i= 0; i<MAX_CLIENTS*2; i++){
    //printf("bu rang gai , you bing ba ni\n");
   
    if(strcmp(IDlist[i], "empty\0")!=0){
      printf("%s\n", IDlist[i]);
    }
  
  
  }


}



char* sort_list(char** IDlist){

  int count=0;
  char* output = (char *)calloc(800 ,sizeof(char));
  char** IDlist_copy = (char **)calloc(MAX_CLIENTS ,sizeof(char*));
  for(int i= 0; i<MAX_CLIENTS; i++){
    //printf("bu rang gai , you bing ba ni\n");
    IDlist_copy[i] = (char *)calloc(100 ,sizeof(char));

    
    if(strcmp(IDlist[i*2], "empty\0")!=0){
      strcpy(IDlist_copy[i], IDlist[i*2]);
      count++;
    }
  
  
  }


  char* temp = (char *)calloc(100 ,sizeof(char));
  for(int i=0;i<count;i++)  
    {//n个数要进行n-1趟比较
    for(int j=0;j<=count-i;j++)          //每趟比较n-i次
      if(*(IDlist_copy[j])>*(IDlist_copy[j+1]))          //依次比较两个相邻的数，将小数放在前面，大数放在后面
      {
        //printf("change here %d %d\n",i, j);
        temp=IDlist_copy[j];
        IDlist_copy[j]=IDlist_copy[j+1];
        IDlist_copy[j+1]=temp;
      }
  }

  for(int i= 0; i<=count+5; i++){
    if(strcmp(IDlist_copy[i], "")!=0){
      // printf(" i=%d   %s\n ",i, IDlist_copy[i]);
    }
    
    // strcat (output,IDlist_copy[i]);
    // strcat (output,"\\n");
  }


  strcat (output,"OK!\n");

  for(int i= 0; i<count+5; i++){
    //printf("%s\n", IDlist_copy[i]);
    if(strcmp(IDlist_copy[i], "")!=0){
      strcat (output,IDlist_copy[i]);
      // printf("+%s\n", IDlist_copy[i]);
      strcat (output,"\n");
      // printf("+%s\n", "\\n");
      // printf("=%s\n",output );
    }
  }


  return output;

}










int command(char* buffer,  char** IDlist, int fd){


  /*

  LOGIN 1 OK!\n
  LOGIN 2 ERROR Already connected\n


  LOGIN 30 ERROR Invalid userid\n

  WHO  3  OK!\nRick\nSummer\n


  SEND 4  FROM ID fd ......

  SEND 5 Invalid ID

  SEND 100 SEND not supported over UDP

  BROADCAST 7



  */




  if(buffer[0] == 'L'&& buffer[1] == 'O'&& buffer[2] == 'G'&& buffer[3] == 'I'&& buffer[4] == 'N'&& buffer[5] == ' '){

    // printf("the command is LOGIN\n");
    char ID[30];
    char fd_number[30];


    for(int i= 6; buffer[i-1]!= '\n'; i++){
      if(buffer[i]!= '\n'){
        ID[i-6]=buffer[i];
      }else{
        ID[i-6]='\0';
      }
      
    }
    // printf("the ID is %s\n", ID);
    printf(" Rcvd LOGIN request for userid %s\n", ID);
    if(strlen(ID)>16||strlen(ID)<4){
      // printf("The ID is invalid\n");
      return 30;
    }

    for(int i=0;i<MAX_CLIENTS*2; i=i+2){
      if(strcmp(IDlist[i], ID)==0){
        // printf("The ID has been LOGIN already\n");
        return 2;


      }else{
        continue;
      }

    }


    for(int i=0;i<MAX_CLIENTS*2; i=i+2){
      //printf("1i=%d\n",i );
      if(strcmp(IDlist[i], "empty\0")==0){
        //printf("2i=%d\n",i );
        strcpy(IDlist[i], ID);

        sprintf(fd_number, "%d", fd);

        strcpy(IDlist[i+1], fd_number);

        break;
      }else{
        continue;
      }
    }
 
    return 1;

  }




  if(buffer[0] == 'W'&& buffer[1] == 'H'&& buffer[2] == 'O'){

    printf(" Rcvd WHO request\n");

    return 3;



  }

  if(buffer[0] == 'L'&& buffer[1] == 'O'&& buffer[2] == 'G'&& buffer[3] == 'O'&& buffer[4] == 'U'
    && buffer[5] == 'T'){
    printf(" Rcvd LOGOUT request\n");

    char fd_number[30];
    sprintf(fd_number, "%d", fd);

    for(int i=1;i<MAX_CLIENTS*2; i=i+2){
      if(strcmp(IDlist[i], fd_number)==0){
        strcpy(IDlist[i], "empty");
        strcpy(IDlist[i-1], "empty");
      }


    }

    return 1;



  }



  if(buffer[0] == 'S'&& buffer[1] == 'E'&& buffer[2] == 'N'&& buffer[3] == 'D'&& buffer[4] == ' '){


  //char* test = "SEND Rick 27\nYes, idiot, I'm right here!";

    char* ID = (char *)calloc(20 ,sizeof(char));

    int number;

    char* message = (char *)calloc(200 ,sizeof(char));





    if(strlen(buffer)>150||*(buffer+10)=='0'){
      printf(" Rcvd SEND request to userid Rick\n");      
      return 40;
    }

    cut_send(buffer, ID,  &number, message);
    printf(" Rcvd SEND request to userid %s\n",ID);

    if(number<1||number>990){
      // printf("We didn't find -----------------------\n" );
      // tcflush(fd, TCIOFLUSH);
      return 40;
    } 


    int found = -1;
    for(int i=0;i<MAX_CLIENTS*2; i=i+2){

          if(strcmp(IDlist[i], ID)==0){
            found = i;

            break;
          }else{
            continue;
          }
    }

    if(found<0){
      // printf("We didn't find %s\n",ID );
      return 5;
    }else{
 
      return 4;
    }


  }

  if(buffer[0] == 'B'&& buffer[1] == 'R'&& buffer[2] == 'O'&& buffer[3] == 'A'
    && buffer[4] == 'D'&& buffer[5] == 'C'&& buffer[6] == 'A'&& buffer[7] == 'S'&& buffer[8] == 'T'){


  //char* test = "SEND Rick 27\nYes, idiot, I'm right here!";

  printf(" Rcvd BROADCAST request\n");


    return 7;

  }


  return 1;

}


struct MoveInput
{

  int newsock;
  fd_set* readfds_D;
  int* client_socket_index_D;
  int* client_sockets;
  struct sockaddr_in client;
  char** IDlist;
};





void * make_move_new(void * Input){
{
    int close1=0;
    char buffer[ BUFFER_SIZE ];   
    int n; 
    
    char* outresult = (char *)calloc(MAXBUFFER,sizeof(char));
    struct MoveInput * Input2 = (struct MoveInput *) Input;

 
      int fd = Input2->newsock;


      while(1){
        bzero(outresult, 200);

        n = recv( fd, buffer, BUFFER_SIZE - 1, 0 );

        if ( n < 0 )
        {
          perror( "recv()" );
        }
        else if ( n == 0 )
        {
          
          int k;
          printf( " Client disconnected\n" );
          close( fd );

          /* remove fd from client_sockets[] array: */
          for ( k = 0 ; k < *(Input2->client_socket_index_D) ; k++ )
          {
            //Found the slot with the fd that is closing
            if ( fd == Input2->client_sockets[ k ] )
            {
              /* found it -- copy remaining elements over fd */
              int m;
              for ( m = k ; m < *(Input2->client_socket_index_D) - 1 ; m++ )
              {
                Input2->client_sockets[ m ] = Input2->client_sockets[ m + 1 ];
              }
              *(Input2->client_socket_index_D) = *(Input2->client_socket_index_D)-1;
              close1=1;
              break;  /* all done */

            }
          }
        }
        else
        {
          // printf("I am in n>0----------\n");
          buffer[n] = '\0';

          int endofcommand = command(buffer, Input2->IDlist, fd);
          if(endofcommand==1){

            strcpy(outresult, "OK!\n");
            send( fd, outresult, strlen(outresult), 0 );


          }else if(endofcommand==2){
            printf(" Sent ERROR (Already connected)\n");
            strcpy(outresult, "ERROR Already connected\n");
            send( fd, outresult, strlen(outresult), 0 );

          }else if(endofcommand==30){
            printf(" Sent ERROR (Invalid userid)\n");
            strcpy(outresult, "ERROR Invalid userid\n");
            send( fd, outresult, strlen(outresult), 0 );

          }else if(endofcommand==3){

            strcpy(outresult, sort_list(Input2->IDlist));
            send( fd, outresult, strlen(outresult), 0 );

          }else if(endofcommand==5){
            printf(" Sent ERROR (Unknown userid)\n");
            strcpy(outresult, "ERROR Unknown userid\n");
            send( fd, outresult, strlen(outresult), 0 );
          

          }else if(endofcommand==40){
            printf(" Sent ERROR (Invalid msglen)\n");
            strcpy(outresult, "ERROR Invalid msglen\n");
            send( fd, outresult, strlen(outresult), 0 );



          }else if(endofcommand==4){

            strcpy(outresult, "OK!\n");

            send( fd, outresult, strlen(outresult), 0 );

            bzero(outresult, 200);

            char* message = (char *)calloc(MAXBUFFER,sizeof(char));

            char* ID = (char *)calloc(20 ,sizeof(char));
            int number;
            
            cut_send(buffer, ID,  &number, message);


            int endfd = find_fd(ID, Input2->IDlist);

            char* new_name = (char *)calloc(20 ,sizeof(char));
            char* fd_number = (char *)calloc(20 ,sizeof(char));

            sprintf(fd_number, "%d", fd);

            find_ID(fd_number, Input2->IDlist);

            strcpy(new_name, find_ID(fd_number, Input2->IDlist));
            sprintf(outresult, "FROM %s %d %s",new_name, number, message );
            char* test3 = (char *)calloc(MAXBUFFER ,sizeof(char));
            strcpy(test3, outresult);
            send( endfd, outresult, strlen(test3), 0 );

          }else if(endofcommand==7){

            strcpy(outresult, "OK!\n");

            send( fd, outresult, strlen(outresult), 0 );

            bzero(outresult, 200);
            char* message = (char *)calloc(MAXBUFFER,sizeof(char));
            int number;
            cut_broadcast(buffer, &number, message);
            char* new_name = (char *)calloc(20 ,sizeof(char));
            char* fd_number = (char *)calloc(20 ,sizeof(char));

            sprintf(fd_number, "%d", fd);

            find_ID(fd_number, Input2->IDlist);

            strcpy(new_name, find_ID(fd_number, Input2->IDlist));
 
            sprintf(outresult, "FROM %s %d %s\n",new_name, number, message );
  

            for(int i=1;i<MAX_CLIENTS*2; i=i+2){
              if(strcmp(Input2->IDlist[i], "empty\0")!=0){

                // printf("%d: send message %s to %d\n",i, message,atoi(Input2->IDlist[i]));
                send( atoi(Input2->IDlist[i]), outresult, strlen(outresult), 0 );

              }

            }

          }


        }
        if(close1 == 1){
          break;
        }
        
        }

      }
 
      return ((void *)0);

}










int main(int argc, char ** argv)
{
  setvbuf( stdout, NULL, _IONBF, 0 );
  if ( argc != 2 )
  {
    fprintf( stderr, "ERROR: Invalid argument(s)\n");
    fprintf( stderr, "USAGE: a.out <m> \n");
    return EXIT_FAILURE;
  }

  long int m = atoi( *(argv+1));
 
  printf(" Started server\n" );

  /* ====== */
  fd_set readfds;
  pthread_t tid[ MAXTHREADS ];
  fd_set readfds_U;
  int client_sockets[ MAX_CLIENTS ]; /* client socket fd list *///这里是不是应该改为只有一个client socket？？？？？？
  int client_socket_index = 0;  /* next free spot */
  /* ====== */


  /* Create the listener socket as TCP socket */
  /*   (use SOCK_DGRAM for UDP)               */
  int sock = socket( PF_INET, SOCK_STREAM, 0 );//socket和bind那个PF_INET需要match么？？？？？？？？？？？？？？？？？？
    /* note that PF_INET is protocol family, Internet */

  if ( sock < 0 )
  {
    perror( "socket()" );
    exit( EXIT_FAILURE );
  }

  /* socket structures from /usr/include/sys/socket.h */
  struct sockaddr_in server_T;
  struct sockaddr_in client;

  server_T.sin_family = PF_INET;
  server_T.sin_addr.s_addr = INADDR_ANY;//htonl( INADDR_ANY );什么时候需要htonl，什么时候不需要？？？？？

  unsigned short port = m;

  /* htons() is host-to-network-short for marshalling */
  /* Internet is "big endian"; Intel is "little endian" */
  server_T.sin_port = htons( port );//htonl( INADDR_ANY );什么时候需要htons？？？？？？？？
  int len = sizeof( server_T );

  if ( bind( sock, (struct sockaddr *)&server_T, len ) < 0 )
  {
    perror( "bind()" );
    exit( EXIT_FAILURE );
  }

  listen( sock, 5 );  /* 5 is number of waiting clients */
  printf( " Listening for TCP connections on port\n" );

  int fromlen = sizeof( client );



  int i;



  int sd;  /* socket descriptor -- this is actually in the fd table! */

  /* create the socket (endpoint) on the server side */
  sd = socket( AF_INET, SOCK_DGRAM, 0 );
                    /*  ^^^^^^^^^^
                       this will set this socket up to use UDP */

  if ( sd == -1 )
  {
    perror( "socket() failed for U" );
    return EXIT_FAILURE;
  }

 
  struct sockaddr_in server_U;
  int length;

  server_U.sin_family = AF_INET;  /* IPv4 */

  server_U.sin_addr.s_addr = htonl( INADDR_ANY );//host to net long int.
           /* any remote IP can send us a datagram */

  /* specify the port number for the server */
  server_U.sin_port = htons( port );  /* a 0 here means let the kernel assign
                                    us a port number to listen on */

  /* bind to a specific (OS-assigned) port number */
  if ( bind( sd, (struct sockaddr *) &server_U, sizeof( server_U ) ) < 0 )
  {
    perror( "bind() failed" );
    return EXIT_FAILURE;
  }

  length = sizeof( server_U );

  /* call getsockname() to obtain the port number that was just assigned */
  if ( getsockname( sd, (struct sockaddr *) &server_U, (socklen_t *) &length ) < 0 )
  {
    perror( "getsockname() failed" );
    return EXIT_FAILURE;
  }

  printf( " Listening for UDP datagrams on port\n");


  char buffer_U[ MAXBUFFER ];
  // char addr_buffer[ ADDRBUFFER ];
  struct sockaddr_in client_U;
  int len_U = sizeof( client_U );
  int backup_len = len_U;




  char** IDlist = (char **)calloc(MAX_CLIENTS*2 ,sizeof(char*));
  for(int i= 0; i<MAX_CLIENTS*2; i++){
    //printf("bu rang gai , you bing ba ni\n");
    IDlist[i] = (char *)calloc(100 ,sizeof(char));
    IDlist[i][0] = 'e';
    IDlist[i][1] = 'm';
    IDlist[i][2] = 'p';
    IDlist[i][3] = 't';
    IDlist[i][4] = 'y';
    IDlist[i][5] = '\0';
    
  }




  while ( 1 )
  {
  

//------------------------------------------------------------------这是给U和T公共部分，考虑select


#if 1
    struct timeval timeout;
    timeout.tv_sec = 0;
    timeout.tv_usec = 200;  /* 2 seconds AND 500 microseconds */
#endif

    FD_ZERO( &readfds );
    FD_SET( sock, &readfds );   /* listener socket, fd 3 */
    //printf( "For TCP: Set FD_SET to include listener fd %d\n", sock );


    FD_ZERO( &readfds_U );
    FD_SET( sd, &readfds_U );   /* listener socket, fd 3 */
 

#if 1

    for ( i = 0 ; i < client_socket_index ; i++ )
    {
      FD_SET( client_sockets[ i ], &readfds );
/*      printf( "Set FD_SET to include client socket fd %d\n",
              client_sockets[ i ] );*/
    }

#endif



    int ready_U = select( FD_SETSIZE, &readfds_U, NULL, NULL, &timeout );

    if ( ready_U != 0 )
    {
      int mt;

      // printf("---------------------------sd recv begin\n");

      mt = recvfrom( sd, buffer_U, MAXBUFFER, 0, (struct sockaddr *) &client_U,
                    (socklen_t *) &len_U );

      if ( mt == -1 )
      {
        // perror( "recvfrom() failed" );
      }
      else
      {
        //inet_ntoa is deprecated, only handles IPV4
        printf( " Rcvd incoming UDP datagram from\n" );
 
        buffer_U[mt] = '\0';   

        char* outresult = (char *)calloc(800 ,sizeof(char));



          int endofcommand = command(buffer_U, IDlist, sd);
          if(endofcommand==1){
            strcpy(outresult, "OK!\n");
            sendto( sd, outresult, strlen(outresult), 0, (struct sockaddr *) &client_U, backup_len );
            //sendto( sd, outresult, strlen(outresult), 0, (struct sockaddr *) &client_U, backup_len );


          }else if(endofcommand==2){
            strcpy(outresult, "ERROR Already connected\n");
            sendto( sd, outresult, strlen(outresult), 0, (struct sockaddr *) &client_U, backup_len );

          }else if(endofcommand==30){
            strcpy(outresult, "ERROR Invalid userid\n");
            // send( fd, outresult, strlen(outresult), 0 );
            sendto( sd, outresult, strlen(outresult), 0, (struct sockaddr *) &client_U, backup_len );

          }else if(endofcommand==3){

            strcpy(outresult, sort_list(IDlist));
            sendto( sd, outresult, strlen(outresult), 0, (struct sockaddr *) &client_U, backup_len );

          }else if(endofcommand==5){
            strcpy(outresult, "SEND not supported over UDP\n");
            sendto( sd, outresult, strlen(outresult), 0, (struct sockaddr *) &client_U, backup_len );
          

          }else if(endofcommand==4){



            strcpy(outresult, "SEND not supported over UDP\n");
            // send( fd, outresult, strlen(outresult), 0 );
            sendto( sd, outresult, strlen(outresult), 0, (struct sockaddr *) &client_U, backup_len );
          }else if(endofcommand==7){

            strcpy(outresult, "OK!\n");

            // send( fd, outresult, strlen(outresult), 0 );
            sendto( sd, outresult, strlen(outresult), 0, (struct sockaddr *) &client_U, backup_len );

            bzero(outresult, 200);





            char* message = (char *)calloc(MAXBUFFER,sizeof(char));
            int number;
            cut_broadcast(buffer_U, &number, message);

            // printf("the message is %s\n", message);

            char* new_name = (char *)calloc(20 ,sizeof(char));
            char* fd_number = (char *)calloc(20 ,sizeof(char));

            sprintf(fd_number, "%d", sd);

            find_ID(fd_number, IDlist);

            strcpy(new_name, "UDP-client");
            // printf("ID------=======================================================================------is %s\n", new_name);


            sprintf(outresult, "FROM %s %d %s",new_name, number, message );
            printf("the output of command is %s, and I am sendind it now.\n",outresult);



            for(int i=1;i<MAX_CLIENTS*2; i=i+2){
              if(strcmp(IDlist[i], "empty\0")!=0){

                printf("%d: send message %s to %d\n",i, message,atoi(IDlist[i]));
                send( atoi(IDlist[i]), outresult, strlen(outresult), 0 );

              }



            }



          }

      }
      

    }







    
#if 1
    int ready = select( FD_SETSIZE, &readfds, NULL, NULL, &timeout );//我个人理解，这个select之后，就是只有一个fd在readfds里面。被选中那个

    if ( ready == 0 )
    {
      
      continue;
    }
#endif


    if ( FD_ISSET( sock, &readfds ) )
    {
      int newsock = accept( sock,
                            (struct sockaddr *)&client,
                            (socklen_t *)&fromlen );
             /* this accept() call we know will not block */
      printf( " Rcvd incoming TCP connection from\n");
      client_sockets[ client_socket_index++ ] = newsock;

      struct MoveInput *pointer=NULL;
     
      pointer = malloc(sizeof(struct MoveInput));
 
      pointer->newsock = newsock;
      pointer->readfds_D = &readfds;
      
      pointer->client_socket_index_D = &client_socket_index;
      pointer->client_sockets = client_sockets;      
      pointer->client = client;
      pointer->IDlist = IDlist;


      pthread_create( &tid[MAXTHREADS-2], NULL, make_move_new, (void*)pointer );

    }

  
  }


  return EXIT_SUCCESS; /* we never get here */
}
