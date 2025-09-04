# Graph-Visualizer

**Github Pages:** [Graph Visualizer Web Application](https://lorenypsum.github.io/graph-visualizer/)

Web application that provides visualization for the execution of algorithms in directed graphs.

This project is a web application that provides visualization for the execution of the **Chu, Liu and Edmonds Algorithm** in directed graphs.
It allows users to input a directed graph and visualize the steps of the algorithm in real-time.


## Cloning the Repository:
To clone the repository, run the following command in your terminal:

```bash 
git clone https://github.com/lorenypsum/graph-visualizer.git
```

## Activate Virtual Environment:

```bash
source .venv/bin/activate
```

## Install Requirements:

```bash
pip install -r requirements.txt
```

## Run Tests:
To run the tests with:

```bash
# For all tests
pytest test_chuliu.py
```

## Visualize Algorithms in Browser:

To visualize the algorithms in the browser, you need to open the `index.html` file in your web browser. You can do this in several ways:

1. **Open the file directly**: Navigate to the directory where `index.html` is located and double-click on it. This should open the file in your default web browser.
    Alternatively, you can right-click on the file and select "Open with" and choose your preferred web browser.
    **Note**: Some browsers may block local file access for security reasons. If you encounter issues, try one of the following methods:
    - Use a different browser (e.g., Chrome, Firefox).
    - Use a local server (see below).
    - Disable security settings in your browser (not recommended for security reasons).
  
2. **Use a code editor**: If you are using a code editor like Visual Studio Code, you can use the Live Server extension to open the file in your browser. Just right-click on the `index.html` file and select "Open with Live Server".
    This will start a local server and open the file in your default web browser.
     **Note**: You may need to install the Live Server extension if you haven't already.
    You can install it from the Extensions Marketplace in Visual Studio Code.

3. **Use a local server**: If you have Python installed, you can use the built-in HTTP server to serve the file. Open a terminal, navigate to the directory where `index.html` is located, and run:

   ```bash
   python -m http.server
   ```

   Then open your web browser and go to `http://localhost:8000/index.html`.

## TODO:

- Melhorar a checagem de dualidade.
- Limpar o código.
- Melhorar os testes (incluir condicional de boilerplate).
- Começar escrever o texto.