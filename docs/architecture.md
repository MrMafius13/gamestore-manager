# 🏛️ GameStore Manager — Arquitectura Técnica

Este documento detalla la arquitectura de software, modelo de datos y patrones de diseño aplicados en el módulo **GameStore Manager** para Odoo 18 Community.

---

## 1. Diagrama de Infraestructura (Docker)

```mermaid
graph TD
    subgraph Host["💻 Host Machine (Windows)"]
        User["🌐 Navegador Web (Usuario)<br>http://localhost:8069"]
        ExtApp["📱 Script / App Externa<br>API REST / XML-RPC"]
        PostgresLocal["🐘 PostgreSQL Local<br>Puerto 5432 (Sin conflicto)"]
    end

    subgraph DockerNet["🐳 Red Docker (bridge)"]
        subgraph OdooService["Contenedor: gamestore_odoo"]
            OdooCore["Odoo 18 Community<br>Python 3.11 / Werkzeug"]
            Addon["Módulo: gamestore_manager<br>/mnt/extra-addons"]
        end

        subgraph DbService["Contenedor: gamestore_db"]
            PostgresContainer["PostgreSQL 16<br>Puerto interno 5432<br>Mapeado a host 5433"]
        end
    end

    User -->|HTTP 8069| OdooCore
    ExtApp -->|REST JSON / XML-RPC| OdooCore
    OdooCore -->|Conexión TCP interna| PostgresContainer
```

* **Aislamiento de Puertos:** el PostgreSQL del contenedor se expone en el puerto `5433` del host, garantizando coexistencia pacífica con cualquier instalación local previa de PostgreSQL en el puerto `5432`.
* **Modo Desarrollo:** Odoo arranca con el parámetro `--dev=reload,xml`, lo que permite recargar el código Python y las vistas XML al guardar los archivos sin reiniciar manualmente el contenedor.

---

## 2. Diagrama Entidad-Relación (Modelo de Datos)

```mermaid
erDiagram
    gamestore_plataforma ||--o{ gamestore_videojuego : "contiene"
    gamestore_desarrolladora ||--o{ gamestore_videojuego : "desarrolla"
    gamestore_genero }o--o{ gamestore_videojuego : "clasifica (M2M)"
    
    gamestore_videojuego ||--o{ gamestore_pedido_linea : "incluido en"
    gamestore_pedido ||--|{ gamestore_pedido_linea : "compuesto por"
    res_partner ||--o{ gamestore_pedido : "realiza (Cliente)"
    res_users ||--o{ gamestore_pedido : "atiende (Vendedor)"

    gamestore_videojuego {
        int id PK
        char name
        many2one plataforma_id FK
        many2one desarrolladora_id FK
        monetary precio
        int stock
        int stock_minimo
        selection estado_stock "disponible, bajo, agotado"
        int unidades_vendidas "computed"
    }

    res_partner {
        int id PK
        char name
        boolean es_cliente_gamestore
        int gamestore_pedido_count "computed"
        monetary gamestore_total_gastado "computed"
    }

    gamestore_pedido {
        int id PK
        char name "PED/2026/0001"
        many2one cliente_id FK
        datetime fecha
        selection estado "borrador, confirmado, pagado, entregado, cancelado"
        monetary total "computed store"
    }

    gamestore_pedido_linea {
        int id PK
        many2one pedido_id FK
        many2one videojuego_id FK
        int cantidad
        monetary precio_unitario "congelado al guardar"
        monetary subtotal "computed"
    }
```

---

## 3. Máquina de Estados del Pedido y Flujo de Stock

```mermaid
stateDiagram-v2
    [*] --> Borrador: Nuevo Pedido
    
    Borrador --> Confirmado: action_confirmar()
    note right of Confirmado
        1. Valida que stock >= cantidad
        2. Descuenta stock del videojuego (-N)
        3. Fija fecha_confirmacion
    end note

    Confirmado --> Pagado: action_pagar()
    Pagado --> Entregado: action_entregar()
    
    Borrador --> Cancelado: action_cancelar() (Wizard)
    Confirmado --> Cancelado: action_cancelar() (Wizard)
    note right of Cancelado
        Si estaba confirmado/pagado:
        Devuelve el stock al inventario (+N)
        Guarda motivo en el chatter
    end note

    Cancelado --> Borrador: action_borrador()
    Entregado --> [*]
```

---

## 4. Patrones de Diseño Aplicados

### A. Herencia de Modelos (`res.partner`)
En lugar de crear un modelo aislado de clientes, se utiliza la **herencia clásica de Odoo** (`_inherit = 'res.partner'`). Esto permite:
* Reutilizar libreta de direcciones, contactos, geolocalización y chatter nativo de Odoo.
* Incorporar campos específicos (`es_cliente_gamestore`, `gamestore_total_gastado`, `gamestore_plataforma_favorita_id`).
* Añadir un *Smart Button* interactivo en la ficha de cualquier contacto.

### B. Desacoplamiento de Transacciones (Cabecera y Líneas)
Estructura tipo `gamestore.pedido` (Cabecera) y `gamestore.pedido.linea` (Detalle). El precio unitario en la línea se precalcula al elegir el videojuego, pero queda **almacenado y congelado**, evitando que futuras subidas de precio en el catálogo alteren el histórico contable de pedidos antiguos.

### C. Vistas SQL para Business Intelligence (`_auto = False`)
El modelo `gamestore.informe.ventas` no genera una tabla en disco. Utiliza el método `init()` para crear una **`VIEW` en PostgreSQL** que une pedidos, líneas y catálogos en una sola consulta optimizada. Sobre ella, Odoo monta vistas de tipo `pivot` (tabla dinámica multidimensional) y `graph` (gráficos de barras y líneas).

### D. Asistentes Transitorios (`TransientModel`)
* `gamestore.reponer.stock.wizard`: Asistente modal en memoria para reposición masiva de inventario con cantidades sugeridas automáticamente.
* `gamestore.cancelar.pedido.wizard`: Asistente para forzar la captura obligatoria de motivos de cancelación antes de revertir los stocks.

### E. Seguridad Basada en Roles (RBAC) y Reglas de Registro
1. **Grupos de Usuario:**
   * `Dependiente`: Operaciones de venta diarias (creación de clientes y pedidos). No puede borrar pedidos ni modificar precios de catálogo.
   * `Encargado`: Acceso total a catálogo, informes analíticos, configuración y asistentes de reposición.
2. **Reglas de Registro (`ir.rule`):** Un dependiente solo puede modificar y gestionar aquellos pedidos donde él figure como `vendedor_id`.
