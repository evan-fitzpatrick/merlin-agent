from merlin import Merlin
from openrouterwrapper import OpenrouterWrapper
import time

system_prompt = open('sysprompt.txt', 'r').read()
model = "deepseek/deepseek-r1-0528:free"

merlin = Merlin(headless=False)
wrapper = OpenrouterWrapper(
	model=model,
	user_credentials=open('openrouterkey-1.txt', 'r').read(),
	system_prompt=system_prompt
)


max_messages = 10
bad_password_message = 'Alas! That password is incorrect!'

for level in range(1,8):
	merlin_message = 'Hello traveler! Ask me anything...'
	wrapper.clear_history(keep_system=True)
	bad_password = False

	print(f'Trying to solve level {level}')

	for i in range(max_messages):
		if bad_password:
			llm_message = wrapper.send_message(bad_password_message)
			bad_password = False
		else:
			llm_message = wrapper.send_message(merlin_message)

		if 'Merlin:' in llm_message:
			merlin_message = merlin.message(llm_message.split('Merlin: ')[-1])
		elif 'Password:' in llm_message:
			password_result = merlin.guess_password(llm_message.split('Password: ')[-1])
			if password_result:
				print(f'Successfully Completed Level {level}!\n')
				break
			else:
				bad_password = True
		else: 
			print(f'!! Invalid Formatting !! {llm_message}')

		if i == max_messages - 1:
			print(f'{model} got to level {level}.')
			break;break


time.sleep(3)
merlin.close()
