/** @type {import('tailwindcss').Config} */
module.exports = {
  // core/**/*.py: os widgets de core/forms.py definem classes nos attrs.
  // static/js/formularios.js: insere o spinner do daisyUI no botão.
  content: ["./templates/**/*.html", "./core/**/*.py", "./static/js/formularios.js"],
  plugins: [require("daisyui")],
  // O tema "conecta" fica em static/css/app.css; nenhum tema embutido é usado.
  daisyui: { themes: false, logs: false },
};
