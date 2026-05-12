const API_URL = "https://mascotas-pied.vercel.app";

// ======================================
// TEST API
// ======================================

async function testAPI() {

    const response = await fetch(API_URL);

    const data = await response.json();

    document.getElementById("apiResponse")
        .textContent = JSON.stringify(data, null, 2);
}

// ======================================
// CARGAR MASCOTAS
// ======================================

async function cargarMascotas() {

    const response = await fetch(`${API_URL}/mascotas`);

    const data = await response.json();

    const contenedor = document.getElementById("mascotas");

    contenedor.innerHTML = "";

    data.data.forEach(mascota => {

        contenedor.innerHTML += `

            <div class="mascota">

                <img src="${mascota.imagen || 'https://placehold.co/600x400'}">

                <h3>${mascota.nombre}</h3>

                <p>${mascota.especie}</p>

                <p>${mascota.edad}</p>

                <p>${mascota.ciudad}</p>

                <p>${mascota.descripcion}</p>

                <button onclick="abrirEditar(
                    ${mascota.id},
                    '${mascota.nombre}',
                    '${mascota.especie}',
                    '${mascota.edad}',
                    '${mascota.ciudad}',
                    '${mascota.descripcion}',
                    '${mascota.imagen}'
                )">
                    Editar
                </button>

                <button onclick="eliminarMascota(${mascota.id})">
                    Eliminar
                </button>

            </div>
        `;
    });
}

// ======================================
// REGISTRAR
// ======================================

document
.getElementById("formMascota")
.addEventListener("submit", async (e) => {

    e.preventDefault();

    const mascota = {

        nombre: nombre.value,

        especie: especie.value,

        edad: edad.value,

        ciudad: ciudad.value,

        descripcion: descripcion.value,

        imagen: imagen.value
    };

    await fetch(`${API_URL}/mascotas`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(mascota)
    });

    cargarMascotas();

    e.target.reset();
});

// ======================================
// ELIMINAR
// ======================================

async function eliminarMascota(id) {

    await fetch(`${API_URL}/mascotas/${id}`, {

        method: "DELETE"
    });

    cargarMascotas();
}

// ======================================
// BUSCAR POR ID
// ======================================

async function buscarMascota() {

    const id = document.getElementById("buscarId").value;

    const response = await fetch(`${API_URL}/mascotas/${id}`);

    const data = await response.json();

    document.getElementById("resultadoBusqueda")
        .textContent = JSON.stringify(data, null, 2);
}

// ======================================
// ABRIR MODAL EDITAR
// ======================================

function abrirEditar(
    id,
    nombre,
    especie,
    edad,
    ciudad,
    descripcion,
    imagen
) {

    modal.style.display = "block";

    editId.value = id;
    editNombre.value = nombre;
    editEspecie.value = especie;
    editEdad.value = edad;
    editCiudad.value = ciudad;
    editDescripcion.value = descripcion;
    editImagen.value = imagen;
}

// ======================================
// CERRAR MODAL
// ======================================

function cerrarModal() {

    modal.style.display = "none";
}

// ======================================
// GUARDAR EDICIÓN
// ======================================

async function guardarEdicion() {

    const id = editId.value;

    const mascota = {

        nombre: editNombre.value,

        especie: editEspecie.value,

        edad: editEdad.value,

        ciudad: editCiudad.value,

        descripcion: editDescripcion.value,

        imagen: editImagen.value
    };

    await fetch(`${API_URL}/mascotas/${id}`, {

        method: "PUT",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(mascota)
    });

    cerrarModal();

    cargarMascotas();
}

// ======================================
// INIT
// ======================================

cargarMascotas();