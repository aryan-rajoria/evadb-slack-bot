# EvaDB Slack Bot

This bot 🤖 allows users to ask questions about PDFs 📄 using EvaDB. 

EvaDB: https://github.com/georgia-tech-db/evadb. 

EvaDB enables software developers to build AI apps in a few lines of code. Its powerful SQL API simplifies AI app development for both structured and unstructured data. EvaDB's benefits include:
- 🔮 Easy to connect EvaDB with your SQL database system and build AI-powered apps with SQL queries
- 🤝 Query your data with a pre-trained AI model from Hugging Face, OpenAI, YOLO, PyTorch, and other AI frameworks
- ⚡️ Faster queries thanks to AI-centric query optimization
- 💰 Save money spent on running models by efficient CPU/GPU use
- 🔧 Fine-tune your AI models to achieve better results

👋 Hey! If you're excited about our vision of bringing AI inside database systems, show some ❤️ by: 
<ul>
  <li> 🐙 giving a ⭐ on our <a href="https://github.com/georgia-tech-db/evadb">EvaDB repo on Github</a>
  <li> 📟 joining our <a href="https://evadb.ai/community">Slack Community</a>
  <li> 🐦 following us on <a href="https://twitter.com/evadb_ai">Twitter</a>
  <li> 📝 following us on <a href="https://medium.com/evadb-blog">Medium</a>
</ul>

## Installation
### Local Host
> Note: requries ngrok

#### 1) Export your Slack Bot Token and Signing Key to the environment
```bash
export SLACK_BOT_TOKEN=<your-slack-token>
export SLACK_SIGNING_SECRET=<you-slack-siging-secret>
```


#### 2) Load the PDF datasets into EvaDB  
Refer ![EvaDB Docs](https://evadb.readthedocs.io/en/stable/)  

#### 3) Start Flask server
```bash
FLASK_APP=slack_client.py FLASK_ENV=development flask run -p <port-number>
```

#### 4) (Optional) Expose your Public IP
```bash
ngrok http <port-number>
```
