Respecto al uso de IA para esta actividad:

- Se usó GPT-5.4 en Cursor (en modo Ask, no Agent).
- En el archivo `test_pricing_service.py`, su uso consistió, principalmente, en:
    - Explicar la diferencia de sintaxis entre `pytest` y `unittest`.
    - Aclarar dudas sobre cómo estructurar tests para _Statement Coverage_.
    - Explicar el uso de `self.assertRaises(...) as context`, y cómo se puede usar para verificar el mensaje de error asociado.
    - Entre otras dudas de menor relevancia.
- En el archivo `test_checkout_service.py`, su uso consistió, principalmente, en:
    - Explicar cómo usar la clase `Mock()` (que resultó ser bastante simple).
    - Explicar el uso de `return_value` para atributos de clase "mockeados".
    - Explicar la existencia de métodos como `assert_called_once()`, `assert_called_once_with()`, entre otros.
    - En general, y sobre todo para este archivo, sirvió como la apoyo para consultar sintaxis y uso de la librería `unittest`. Antes de la actividad entendía la teoría, pero no sabía bien como implementarla a nivel de código.
- Finalmente, sirvió para hacer un _double-check_ a que todos los _branches_ estuvieran bien cubiertos por ambos _test suites_. A priori pensé que sí, pero fue capaz de detectar algunos que se me habían pasado, lo que me sirvió para resolver algunas dudas conceptuales que tenía y resolverlos.

PD (no relacionado a IA): corrí `ruff check .` y `ruff format .` como hago de costumbre, y se modificaron algunos archivos base (como `checkout.py`, `models.py`, y `pricing.py`), pero la funcionalidad está intacta.