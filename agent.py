from merlin import Merlin
from openrouterwrapper import OpenrouterWrapper
import time

system_prompt = open('sysprompt.txt', 'r').read()

merlin = Merlin(headless=False)
wrapper = OpenrouterWrapper(
	model="deepseek/deepseek-chat-v3.1:free",
	user_credentials="redacted",
	system_prompt=system_prompt
)

max_messages = 3
merlin_message = 'Hello traveler! Ask me anything...'
for i in range(max_messages):
	llm_message = wrapper.send_message(merlin_message)
	if 'Merlin:' in llm_message:
		merlin_message = merlin.message(llm_message.split('Merlin: ')[-1])
	elif 'Password:' in llm_message:
		password_result = merlin.guess_password(llm_message.split('Password: ')[-1])
		if password_result:
			print(f'PRAISE THE LORD JESUS WE DID IT!!!!')
			break
	else: 
		print(f'!! Invalid Formatting !! {llm_message}')

#wrapper.clear_history()  # or wrapper.clear_history(keep_system=True)
#print(wrapper.history)

time.sleep(5)
merlin.close()
