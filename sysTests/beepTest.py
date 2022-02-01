import os

#os.system('( speaker-test -t sine -c 2 -s 2 -f 880 & TASK_PID=$! ; sleep 0.5 ; kill -s $TASK_PID ) > /dev/null')

print('Hello')
os.system('( speaker-test -t sine -c 2 -s 2 -f 880 & TASK_PID=$! ; sleep 0.5) > /dev/null')
print('Goodbye')
