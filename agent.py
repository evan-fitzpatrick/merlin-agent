from merlin import Merlin
from openrouterwrapper import OpenrouterWrapper

system_prompt = open('sysprompt.txt', 'r').read()

merlin = Merlin(headless=False)
wrapper = OpenrouterWrapper(
	model="deepseek/deepseek-chat-v3.1:free",
	user_credentials="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",
	system_prompt=system_prompt
)

max_messages = 10
merlin_message = 'Hello, my name is Merlin.'
for i in range(max_messages):
	llm_message = wrapper.send_message(merlin_message)
	if 'Merlin:' in llm_message:
		merlin_message = merlin.message(llm_message.split('Merlin: ')[-1])
	elif 'Password:' in llm_message:
		password_result = merlin.guess_password(llm_message.split('Password: ')[-1])
	else: 
		print(f'!! Invalid Formatting !! {llm_message}')

#wrapper.clear_history()  # or wrapper.clear_history(keep_system=True)

time.sleep(5)
merlin.close()
