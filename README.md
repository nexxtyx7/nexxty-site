# NEXXTY ONE

CRM de prospecção de negócios com Streamlit.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Render

Build:
```bash
pip install -r requirements.txt
```

Start:
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

O arquivo `restaurantes.csv` é criado automaticamente na primeira execução.
