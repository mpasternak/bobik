bobik, bot preanestetyczny

(C) 2024 Michał PASTERNAK

Licencja MIT

Instrukcja obsługi
------------------

```shell
$ poetry install
$ export PYTHONPATH=src
$ python -m bobik.cli
```

Zadziała też:
```shell
$ python -m bobik.cli
```

Wymaga zmiennych srodowiskowych z kluczami do API Anthropic (``ANTHROPIC_API_KEY``) lub 
OpenAI (``OPENAI_API_KEY``)...

Opcjnalnie wymaga bazy danych PostgreSQL, gdzie może zapisywać historię chat. 
