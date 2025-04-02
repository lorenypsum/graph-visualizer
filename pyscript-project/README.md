# PyScript Project

## Overview
This project is a web application built using PyScript, which allows for the integration of Python code into web applications. The application consists of several pages, including a cart page and a user page, and utilizes HTML templates for rendering content.

## Project Structure
```
pyscript-project
├── static
│   ├── css
│   │   └── styles.css
│   ├── js
│   │   └── scripts.js
├── templates
│   ├── page1.html
│   ├── page2.html
│   └── index.html
├── main.py
├── pyscript.json
└── README.md
```

## Files Description
- **static/css/styles.css**: Contains the CSS styles for the project, defining the visual appearance of the web pages.
- **static/js/scripts.js**: Contains JavaScript code for client-side functionality, such as handling user interactions and dynamic content updates.
- **templates/page1.html**: HTML template for the cart page, rendered when the user navigates to `localhost:8000/page1`.
- **templates/page2.html**: HTML template for the user page, rendered when the user navigates to `localhost:8000/page2`.
- **templates/index.html**: Main HTML template for the home page of the application.
- **main.py**: Entry point of the PyScript application, containing logic for handling requests and rendering the appropriate templates.
- **pyscript.json**: Configuration file for the PyScript project, specifying dependencies, permissions, and application settings.

## Setup Instructions
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Ensure you have Python installed on your system.
4. Run the application using the command:
   ```
   python main.py
   ```
5. Open your web browser and go to `localhost:8000` to access the application.

## Usage Guidelines
- Navigate to `localhost:8000/cart` to view the cart page.
- Navigate to `localhost:8000/user` to view the user page.
- Modify the CSS and JavaScript files in the `static` directory to customize the appearance and functionality of the application.