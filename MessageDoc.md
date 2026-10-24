# Ollama Message:

model: The model used to generate a response

created_at: A timestamp of when ollama generated the response in UTC

message: The reply from ollama/the model structured as {"role": "assistant", "content": "..."}

done: True/False whether generation has finished

done_reason: why generation has stopped, "stop" meaning it naturally finished

total_duration: total time spent for the entire request (load_duration + prompt_eval_duration + eval_duration)

load_duration: How long it took to load the model into memory/VRAM

prompt_eval_count: How many tokens the input is measured as, includes message history we send with our message

prompt_eval_duration: Time spent processing/understanding the input in nanoseconds

eval_count: Tokens the model used to generate a response

eval_duration: time spent generating the output tokens in nanoseconds. 

---
# Tokens per Second

eval_count / (eval_duration in seconds) = Tokens per second (TPS)
