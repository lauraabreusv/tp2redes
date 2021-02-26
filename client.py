import threading 
import socket
import sys
import struct
import os 
import timeit
import time

N_THREADS = 3
mutex = threading.Lock()
# running_threads = 0
# global running_threads

def check_filename(f):
	if len(f) > 15: 
		return False

	if not len(f) == len(f.encode()):
		return False

	if f.count('.') != 1:
		return False

	ext = f.split('.')[1]
	if len(ext) > 3:
		return False

	return True


def send_msg(s, msg):
	s.sendall(msg)

def recv_msg(s, format_=None):
	message = s.recv(1024)
	if format_ is not None:
		data = struct.unpack(format_, message)
	else:
		data = message.decode()

	return data

def send_file(s, s_udp, header, data, udp_port, n_exec):
	if(s_udp.sendto(header + data, ('', udp_port))):
		try:
			#oi tudubm
			message = s.recv(1024)
		except:
			if n_exec == 5:
				print('cant send package')
				s.close() #ver aqui pq ne, mas acho q so desiste
				exit()
			n_exec+=1
			return send_file(s, s_udp, header, data,  udp_port, n_exec)
		# print
		ack_data = struct.unpack('2s i', message)
		print(ack_data[1])

		# mutex.acquire()
		# running_threads-=1
		# mutex.release()
		return

	else:
		if n_exec == 5:
			print('cant send pack')
			s.close() #ver aqui pq ne, mas acho q so desiste
			exit()
			return
		n_exec+=1
		return send_file(s, s_udp, header, data,  udp_port, n_exec)


def protocol(s, file, filename):
	#colocar mil try except no caso de vir no formato errado (ai avisa e fodase os testes automaticos)
	#first part
	hello_msg = '01'
	message = b''
	message += str.encode(hello_msg)

	send_msg(s, message)

	#second part
	unpacked_data = recv_msg(s, '2s i')
	print(unpacked_data)

	if unpacked_data[0].decode() != '02':
		print(unpacked_data[0])
		exit()

	udp_port = unpacked_data[1]
	print(udp_port)

	s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#third part
	info_msg = b'03'
	filenameb = filename.encode()
	size = os.path.getsize(filename)

	if len(str(size)) > 8:
		print('arquivo grande d+')
		exit()

	message = struct.pack('2s ' + str(len(filename)) + 's i', info_msg, filenameb, size)
	send_msg(s, message)

	unpacked_data = recv_msg(s)
	if unpacked_data != '04':
		print('nao oquei')
		print(unpacked_data)
		exit()

	file_msg = b'06'
	n_seq = 0

	header = struct.pack('2s i', file_msg, n_seq)
	data = f.read(1024) #conf os numeros dps
	s.settimeout(1)

	thread_list = []
	# global running_threads
	# running_threads = 0
	while(data):
		#aqui eu faço os bagui mas aqui tenho q receber

		#acho q isso funciona (sai automatico da lista pq a thread morre)		

		while len(thread_list) >= N_THREADS:
			thread_list = [t for t in thread_list if not t.is_alive()]

		# mutex.acquire()
		# running_threads+=1
		# mutex.release()
		thread = threading.Thread(target = send_file, args=(s, s_udp, header, data, udp_port, 0)) 
		thread_list.append(thread)
		thread.daemon = True
		thread.start()
		# thread.join()

		data = f.read(1024)
		n_seq+=1
		header = struct.pack('2s i', file_msg, n_seq)
		
	while len(thread_list) > 0:
		thread_list = [t for t in thread_list if not t.is_alive()]

	print('sai?')
	s.settimeout(None)		
	unpacked_data = recv_msg(s)
	if unpacked_data != '05':
		print('nao fim')
		exit()

	print('fechando')
	s.close()
	#aqui fazer a parte de conferir o file (ver s eé aqui msm ou main)
	#mas preciso conferir o file name



if __name__ == "__main__":
	if len(sys.argv) < 4:
		print('missing address, port or filename')
		exit()

	addr = sys.argv[1]
	port = sys.argv[2]
	filename = sys.argv[3]

	running_threads = 0

	if not check_filename(filename):
		print('Nome nao permitido')
		exit()

	#ainda n
	f = open(filename, 'rb')
	if not f:
		print('file not found')
		exit()

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((addr, int(port)))
	
	protocol(s, f, filename)




