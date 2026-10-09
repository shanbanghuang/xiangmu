.PHONY: help setup lab01 lab02 fuzz lint clean

help:
	@echo "make setup   安装依赖"
	@echo "make lab01   启动靶场 01：直接提示注入      -> http://127.0.0.1:8001/docs"
	@echo "make lab02   启动靶场 02：间接注入/RAG投毒  -> http://127.0.0.1:8002/docs"
	@echo "make fuzz    对运行中的靶场跑注入 payload 库"

setup:
	pip install -r requirements.txt

lab01:
	python labs/lab01-direct-injection/app.py

lab02:
	python labs/lab02-indirect-injection/app.py

fuzz:
	python toolkits/inject_fuzzer.py --url http://127.0.0.1:8001/chat

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
