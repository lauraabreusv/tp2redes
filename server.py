import threading 
import socket
import sys
import struct
import select

UDP = 5000

def client(conn, udp_port):
	message = conn.recv(1024) #ver dps a qtd de bytes

	if str(message.decode()) != '01':
		conn.close()
		return

	s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s_udp.bind(('', udp_port))

	connection_msg = b'02'
	message = struct.pack('2s i', connection_msg, udp_port)

	conn.sendall(message)

	message = conn.recv(1024)
	fname_len = len(message) - 6

	unpacked_data = struct.unpack('2s ' + str(fname_len) + 's i', message)

	if unpacked_data[0].decode() != '03':
		print(unpacked_data[0])
		exit()

	filename = unpacked_data[1].decode()
	filesize = unpacked_data[2]

	print(filename, filesize)

	#gambiarra pra testar, dps mudar:
	filename_splited = filename.split('.') 
	filename = filename_splited[0] + 'out.' + filename_splited[1]
	f = open(filename, 'wb')

	#antes disso eu tenho que alocar os trem tudo ja mas ne problema para the future
	ok_msg = '04'
	message = b''
	message += str.encode(ok_msg)

	conn.sendall(message)
	ack_msg = b'07'

	count_ack = 0

	while(True):
		#stop and wait
		ready = select.select([s_udp], [], [], 3) #3 sec timeout
		if ready[0]:
			data, addr_udp = s_udp.recvfrom(1024)

			if data is None:
				f.close()
				break

			#ver um timeout ou pensar nisso dps, agr quero resolver o problema imediato
			header = struct.unpack('2s i', data[:8])
			file_content = data[8:]

			#dps ver se confiro o 07
			n_seq = header[1]

			print('n seq and count ack:')
			print(n_seq, count_ack)
			if n_seq != count_ack:
				continue #tenta receber dnv ate receber oq deve

			f.write(file_content)
			
			confirm_message = struct.pack('2s i', ack_msg, n_seq)
			conn.sendall(confirm_message)

			count_ack+=1
		else:
			f.close()
			break


	#aqui fazer os bagui td
	fim_msg = '05'
	message = b''
	message += str.encode(fim_msg)

	conn.sendall(message)

	conn.close()


if __name__ == "__main__":

	if len(sys.argv) < 2:
		print('missing port')
		exit()
	# addr = sys.argv[1]
	port = sys.argv[1]

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', int(port)))
	s.listen()

	thread_list = []
	while True:
		conn, addr_conn = s.accept()
		UDP+=10
		udp_port = UDP
		thread = threading.Thread(target = client, args=(conn,udp_port))
		thread_list.append(thread)
		thread.start()

