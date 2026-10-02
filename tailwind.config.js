/** @type {import('tailwindcss').Config} */
module.exports = {
  // core/**/*.py: os widgets de core/forms.py definem classes nos attrs.
  content: ["./templates/**/*.html", "./core/**/*.py"],
  plugins: [require("daisyui")],
  // O tema "conecta" fica em static/css/app.css; nenhum tema embutido é usado.
  daisyui: { themes: false, logs: false },
};
