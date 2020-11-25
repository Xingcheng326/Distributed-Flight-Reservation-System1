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
