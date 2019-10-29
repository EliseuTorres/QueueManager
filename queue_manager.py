# Copyright 2018 Eliseu Silva Torres
#
# This file is part of BAMSDN.
#
# BANSDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BANSDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MininetWeb.  If not, see <http://www.gnu.org/licenses/>.



import os
import subprocess
	
class QueueManager(object):
	swtich_port = ""
	MAX_BW = 0
	num_queue = 0
	queue_bw = []
	queue_id = []
	list_queue = []
	
	def __init__(self, switch_port, max_bw = 0, num_queue = 0, queue_bw = 0):
		if max_bw != 0 and num_queue != 0 and queue_bw != 0:
			self.set_switch_port(switch_port)
			self.define_queue(max_bw, num_queue, queue_bw)
		else:
			self.set_switch_port(switch_port)
	
	
	def set_switch_port(self, switch_port):
		if not self.swtich_port:
			self.switch_port = switch_port
	
	def get_switch_port(self):
		return self.switch_port	
	
	def set_max_bw(self, max_bw):
		self.change_max_bw = False
		
		if self.MAX_BW != 0 or self.MAX_BW != max_bw:
			self.MAX_BW = max_bw
			self.change_max_bw = True
	
	def get_max_bw(self):
		return self.MAX_BW
			
	def set_num_queue(self, num_queue):
		self.change_num_queue = False
		if self.num_queue != num_queue:
			self.num_queue = num_queue
			self.change_num_queue = True
	
	def update_queue(self, new_bw):
		self.num_queue += 1
		self.queue_bw.append(new_bw)
		self._define_queue()
		
	
	
	def get_num_queue(self):
		return self.num_queue
		
	def set_queue_bw(self, queue_bw):
		self.change_queue_bw = False
		if self.queue_bw != queue_bw:
			self.queue_bw = queue_bw
			self.change_queue_bw = True


	def set_list_queue(self, list_queue):
		self.list_queue = list_queue
	
	def	define_queue(self, max_bw, num_queue, queue_bw):
		self.set_max_bw(max_bw)
		self.set_num_queue(num_queue)
		self.set_queue_bw(queue_bw)
		
		if self.change_num_queue or self.change_queue_bw or self.change_max_bw:
			self._define_queue()
			
		
	def _define_queue(self):
		if self._check_defined_queue():
			self._clear_queue()
			self._destroy_queue()
	
		if len(self.queue_bw) == self.num_queue:
    
			command =  "ovs-vsctl -- set Port " + self.switch_port +" qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=" + str(self.MAX_BW) + " queues="
			for q in range(self.num_queue):
				command += "" + str(q) + "=@q" + str(q)
				if q + 1 < self.num_queue:
					command += ","
			for q in range(self.num_queue):
				command += " -- --id=@q" + str(q) + " create Queue other-config:min-rate=" + str(self.queue_bw[q]) + " other-config:max-rate=" + str(self.queue_bw[q])
			
			p = os.popen(command)
			
			for each in p:
				self.queue_id.append(each)	
		else:
			print "Queue has not created, check if the amount of queue match with the number of queue bandwitdh"
			
	def update_queue(self):
		
		if self._check_defined_queue():
			self._clear_queue()
			self._destroy_queue()
	
		if len(self.queue_bw) == len(self.list_queue):
    
			command =  "ovs-vsctl -- set Port " + self.switch_port +" qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=" + str(self.MAX_BW) + " queues="
			for q in range(len(self.queue_bw)):
				command += "" + str(self.list_queue[q]) + "=@q" + str(self.list_queue[q])
				if q + 1 < len(self.queue_bw):
					command += ","
			for q in range(len(self.queue_bw)):
				command += " -- --id=@q" + str(self.list_queue[q]) + " create Queue other-config:min-rate=" + str(self.queue_bw[q]) + " other-config:max-rate=" + str(self.queue_bw[q])
			
			p = os.popen(command)
			
			for each in p:
				self.queue_id.append(each)
		else:
			print "Queue has not created, check if the amount of queue match with the number of queue bandwitdh"

	
	def _clear_queue(self):	
		command = "ovs-vsctl -- clear Port " + str(self.switch_port) + " qos"
		p = os.popen(command)
	
	def _destroy_queue(self):
		command = "ovs-vsctl -- --all destroy QoS -- --all destroy Queue"
		p = os.popen(command)
		self.queue_id = []
	
	def _remove_queue(self):
		q_id = self.queue_id.pop(0)
		command = "ovs-vsctl -- destroy qos " + str(q_id)
		p = os.popen(command)
		
		for i in range(len(self.queue_id)):
			q_id = self.queue_id.pop()
			print q_id
			command = "ovs-vsctl -- destroy queue " + str(q_id)
			p = os.popen(command)
			
	
	def _check_defined_queue(self):
		command = "ovs-vsctl list queue"
		p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	
		if p.stdout.read():
			return True
		else:
			return False
