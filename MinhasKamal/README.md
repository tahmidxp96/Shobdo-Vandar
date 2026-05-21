# MinhasKamal Bengali Dictionary Staging 📚🇧🇩

This folder holds the high-coverage CSV source file for the **MinhasKamal Bengali Dictionary**.

---

## ⚖️ License & Attribution

* **Original Creator/Author:** Minhas Kamal
* **Original Repository:** [MinhasKamal/BengaliDictionary](https://github.com/MinhasKamal/BengaliDictionary)
* **License:** MIT License
* **Copyright Notice:**
  ```text
  Copyright (c) 2017 Minhas Kamal. All rights reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
  ```

---

## 🛠️ Pipeline Integration

The compilation script `kindle_dictionary_builder.py` automatically processes the `BengaliDictionary_93.csv` file:
1. Parses each English headword and its comma-separated list of Bangla meanings.
2. Formats and normalizes the meanings, separating synonym clusters to build a clean index mapping.
3. Ingests all `93,421` records into the master builder lexicon.
