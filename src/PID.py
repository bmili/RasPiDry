#!/usr/bin/python

from pid import pidpy as PIDController
set_point=40
cycle_time=2.2
k_param=10
k_param=10
i_param=1.8
i_param=33
d_param=5
temp_ma=12

pid = PIDController.pidpy(cycle_time, k_param, i_param, d_param) #init pid
for i in range (10,33):
 duty_cycle = pid.calcPID_reg4(i+temp_ma, set_point, True) #ogrevalna stopnja cikla
 print "cycle_time, k_param, i_param, d_param,duty_cycle,temp_ma, set_point", cycle_time, k_param, i_param, d_param,duty_cycle,temp_ma+i, set_point
