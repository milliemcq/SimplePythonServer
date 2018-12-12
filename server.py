import socket
import sys
import time
import logging

logging.basicConfig(filename='server.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(threadName)-10s %(message)s',)


def check_map_for_data(artist, artist_map):
    if artist in artist_map.keys():
        return str(artist_map[artist])
    else:
        return 'No such artist exists'


#Function which formats the textfile correctly (could definitely be more efficient
def create_data_list(data):
    song_list = []
    #print(data)
    for i in range(len(data)):
        item = data[i]
        #print(item)
        item = item.lower()
        item = item.replace("\n", "")
        if len(item) != 0:
            #print(item + '\n')
            if item[0].isdigit():
                item = item[4::]
                if item[-1].isdigit():
                    song_list.append(item)
                elif data[i+1][-1].isdigit():
                    combined_string = data[i] + data[i+1]
                    i += 1
                    song_list.append(combined_string)
            i += 1

    broken_up_items_list = []
    for str in song_list:
        broken_string = str.split("  ")
        #print(len(broken_string))
        broken_string = list(filter(None, broken_string))
        if len(broken_string) == 2:
            continue
        broken_up_items_list.extend(broken_string)


    #print(broken_up_items_list)
    #broken_up_items_list = list(filter(None, broken_up_items_list))
    #print("Final List:")
    #print(broken_up_items_list)
    return broken_up_items_list


def convert_list_to_tuples(list):

    as_map = {}
    i = 0
    while(i < len(list)):
        song_name = list[i]
        artist_name = list[i+1].strip()
        if artist_name in as_map:
            as_map[artist_name].append(song_name)
        else:
            new_list = []
            new_list.append(song_name)
            as_map[artist_name] = new_list
        i += 3
    return as_map


def create_artist_dictionary(data):
    data_as_list = create_data_list(data)
    artist_dict = convert_list_to_tuples(data_as_list)
    return artist_dict



def read_in_text_file():
    f = open("100worst.txt", 'r')
    data = f.readlines()

    #print(data)
    list_of_tuples = create_artist_dictionary(data)
    #print(list_of_tuples)
    return list_of_tuples


#PROGRAM STARTS HERE

artist_map = read_in_text_file()
#print(artist_map)


#create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Bind the socket to the port
working = False
new_port = 10004
while not working:
    try:
        working = True
        int_port = int(new_port)
        server_address = ('localhost', int_port)
        sock.bind(server_address)
    except:
        working = False
        print("This port is busy")
        new_port = input("What is the new port number you would like to use?")



logging.info('starting up on %s port %s' % server_address)
print('server started')


# Listen for incoming connections
sock.listen(1)


while True:
    # Wait for a connection
    print("Listening for incoming connections")
    logging.info('waiting for a connection')

    try:

        #Try accepting connection from the client
        connection, client_address = sock.accept()
        logging.info('Incoming client request from %s' % str(client_address))
        print("Successful connection from" + str(client_address))
        logging.info('Successful Connection from %s' % str(client_address))

        #start connection timer
        connection_time = time.time()
        client_connection_start = time.time()
    except:
        print("Unsuccessful connection from" + str(client_address))
        logging.info('Unsucessful Connection from %s' % str(client_address))

    try:
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(4096)
            if data:
                decoded_data = data.decode('UTF-8')
                logging.info('received "%s"' % data)
                print('received "%s"' % data)

                #Check the client hasn't requested a quit from the server
                if decoded_data == 'quit':

                    #if client has requested quit, close connection after informing client with data '2'
                    connection.sendall(str.encode('2'))

                    #calculate time client was connected and log this information
                    final_connection_time = time.time() - connection_time
                    print('The client was connected for %s seconds' % final_connection_time)
                    logging.info('The client was connected for %s seconds' % final_connection_time)

                    logging.info('The client has disconnected')
                    logging.info("Closing the connection")
                    connection.close()
                    break

                #Server sends a '1' to the client to confirm data receipt
                print("Confirming client data recieved")
                connection.sendall(str.encode('1'))

                #checks for the recieved name in artist-song dictionary
                result = check_map_for_data(decoded_data, artist_map)

                #sends result back to the client (either songs or 'no results')
                result = str.encode(result)
                logging.info('sending data %s back to the client' % result)
                connection.sendall(result)
            else:
                logging.info('no more data from' % str(client_address))
                print("No more data")
                break
        break

    except:
        #Break the connection if fails
        logging.info('Connection Failed')
        print("Connection Failed")
        connection.close()



print("Server Connection Closed")
print("Program Terminated")