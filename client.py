import socket
import sys
import time
import logging

#create the log file
logging.basicConfig(filename='client.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(threadName)-10s %(message)s',)


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
working = False
new_port = 10004
#keep trying new ports until one works
while not working:
    try:
        working = True
        server_address = ('localhost', int(new_port))
        logging.info('connecting to %s port %s' % server_address)
        sock.connect(server_address)
    except:
        working = False
        logging.info("Connection Unsucessful")
        new_port = input("Connection Unsuccessful, try a new port: ")
        # Connect the socket to the port where the server is listening

logging.info("Connection to the Server at port %s successful" % str(server_address))
print("Connection Successful")
try:
    #Get artist name from input, send it to the client and start the timer
    artist_name = input("Please give me the name of an artist: ")
    while artist_name == "":
        print("Cannot input empty string")
        artist_name = input("Please give me the name of an artist: ")
    artist_name = artist_name.lower()
    logging.info('sending "%s"' % artist_name)
    artist_name = str.encode(artist_name)
    data_sent = time.time()
    sock.send(artist_name)


    while True:

        # Look for the response
        while True:

            #get information from the server
            data = sock.recv(1024)
            result = data.decode('UTF-8')

            #Server sends '1' to confirm recieved client's request
            if result == '1':
                print("Data successfully received by the server")
                logging.info("Data successfully received by the server")
                continue
            #Server sends '2' to confirm closure of the connection
            elif result == '2':
                print('Server Connection Closed')
                logging.info("Server Connection Closed")
                break
            else:
                #calculate the time it took the server to respond to the request
                time_to_recieve = time.time() - data_sent
                logging.info('Server response recieved')
                logging.info('The server took %s to respond to the request' % time_to_recieve)
                print('The server took %s to respond to the request' % time_to_recieve)

                #calculate the length of the response
                logging.info('The response length was %s bytes' % sys.getsizeof(result))
                print('The response length was %s bytes' % sys.getsizeof(result))

                #output the data revieved
                print('Received "%s"' % result)
                logging.info('received "%s"' % result)
                break

        #Ensure the user must type quit to close the connection, until the user
        if result != '2':
            quit = input("Enter 'quit' to break the server connection: ")
            if quit.lower() == 'quit':
                sock.send(str.encode('quit'))
                break
            while quit.lower() != 'quit':
                print('Incorrect Input')
                quit = input("Enter 'quit' to break the server connection: ")
                if quit.lower() == 'quit':
                    sock.send(str.encode(quit))
            break
except:
    print("Connection Error")
    logging.info("Connection Error")


print("Program Terminated, Connection Closed")