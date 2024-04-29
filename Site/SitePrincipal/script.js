// Variáveis globais
const header = document.querySelector("header");
const navbarLinks = document.querySelectorAll('.navbar a');
const menuIcon = document.getElementById("menu-icon");
const navbar = document.querySelector(".navbar");

// Header transparente ao rolar
window.addEventListener("scroll", function () {
    header.classList.toggle("sticky", window.scrollY > 60);
});

// Rola suavemente para a seção correspondente ao clicar nos links da barra de navegação
function scrollToSection(targetId) {
    const targetElement = document.getElementById(targetId);

    if (targetElement) {
        const offsetTop = targetElement.offsetTop;
        const offsetHeader = header.clientHeight;
        const offset = offsetTop - offsetHeader;

        window.scrollTo({
            top: offset,
            behavior: 'smooth',
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Link da seta
    const arrowLink = document.querySelector('.arrow a');
    arrowLink.addEventListener('click', function (e) {
        e.preventDefault();
        scrollToSection(arrowLink.getAttribute('href').substring(1));
    });

    // Links da barra de navegação
    navbarLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            scrollToSection(link.getAttribute('href').substring(1));
        });
    });
});

// Atualiza a classe 'show' na barra de navegação quando um link é clicado (para dispositivos móveis)
navbarLinks.forEach(link => {
    link.addEventListener("click", function () {
        navbar.classList.remove("show");
    });
});

// Projeto responsivo
menuIcon.addEventListener("click", function () {
    navbar.classList.toggle("show");
});

navbar.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", function () {
        navbar.classList.remove("show");
    });
});

document.addEventListener("click", function (event) {
    if (!navbar.contains(event.target) && !menuIcon.contains(event.target)) {
        navbar.classList.remove("show");
    }
});

// Fecha a barra de navegação ao rolar
window.addEventListener("scroll", function () {
    navbar.classList.remove("show");
});
