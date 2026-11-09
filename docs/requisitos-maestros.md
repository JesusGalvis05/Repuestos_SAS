<!-- Requisitos conservados del documento proporcionado, adaptados al cambio obligatorio de stack. No implica que estén implementados. -->

# PROMPT MAESTRO — JG REPUESTOS
## Sistema web de gestión comercial e inventario de repuestos automotrices

### 1. Rol de la IA

Actúa como un equipo senior de desarrollo compuesto por:

- Arquitecto de software.
- Desarrollador backend especializado en Python y FastAPI.
- Desarrollador frontend especializado en React y TypeScript.
- Ingeniero de bases de datos PostgreSQL.
- Diseñador UX/UI.
- Ingeniero de calidad y pruebas de software.
- Analista de procesos comerciales y gestión de inventarios.

Tu objetivo es **diseñar e implementar desde cero un sistema web profesional, seguro, escalable y funcional para JG Repuestos**, un negocio colombiano dedicado a la comercialización de repuestos automotrices.

Este sistema tiene dos propósitos:

1. Utilizarse realmente en la administración del negocio.
2. Servir como proyecto universitario de Ingeniería de Software, con arquitectura, documentación, pruebas y buenas prácticas.

No existe actualmente código fuente, base de datos, infraestructura ni proyecto inicial. Todo debe construirse desde cero.

No quiero únicamente diseños, explicaciones o ejemplos. Quiero una aplicación funcional, ejecutable y preparada para evolucionar.

### 2. Tecnologías obligatorias

**Backend**
- Python 3.12 o superior.
- FastAPI, con versiones estables y mantenidas.
- RBAC comprobado en backend, JWT y sesiones revocables.
- SQLAlchemy 2.0 y psycopg.
- Pydantic v2 y pydantic-settings.
- JWT con access tokens de corta duración y mecanismo seguro de renovación de sesión.
- Alembic para migraciones.
- pyproject.toml, pip y dependencias fijadas.
- OpenAPI y Swagger UI.

**Frontend**
- React con TypeScript.
- Vite.
- Tailwind CSS.
- React Router.
- TanStack Query.
- React Hook Form y Zod.
- Axios o cliente HTTP centralizado.
- Librería de componentes consistente y mantenida.
- Recharts para gráficos.

**Base de datos e infraestructura**
- PostgreSQL.
- Docker y Docker Compose para entorno local.
- Archivos `.env.example`.
- Pruebas automatizadas.
- Git y estructura preparada para GitHub.

Usa una arquitectura **API-first**, con endpoints REST versionados bajo `/api/v1`, para permitir que una futura aplicación móvil consuma los mismos servicios.

La arquitectura inicial será un **monolito modular**, evitando microservicios innecesarios.

### 3. Módulo de autenticación y usuarios

Implementar un sistema completo de acceso.

Funcionalidades:

- Inicio y cierre de sesión.
- Contraseñas almacenadas mediante hashing seguro.
- Usuarios activos e inactivos.
- Cambio de contraseña.
- Perfil del usuario.
- Registro de último acceso.
- Control de sesiones.
- Permisos por módulo y operación.
- Protección contra intentos repetidos de autenticación.
- Auditoría de operaciones sensibles.

Roles iniciales:

**Administrador:** acceso completo a configuración, usuarios, proveedores, costos, inventario, compras, ventas y reportes.

**Socio:** acceso a indicadores financieros, utilidades, inventario, compras y ventas según sus permisos.

**Vendedor:** acceso al catálogo, disponibilidad, clientes y ventas. No debe acceder a costos internos ni utilidades salvo autorización explícita.

**Inventario:** acceso a productos, entradas, salidas, ajustes y movimientos de existencias.

Implementar RBAC en el backend; ocultar elementos en el frontend no sustituye la autorización del servidor.

### 4. Módulo de productos y repuestos

Cada repuesto debe existir como un producto único dentro del catálogo interno, independientemente de cuántos proveedores lo comercialicen.

Campos sugeridos:

- Identificador interno UUID.
- SKU único.
- Código de barras opcional.
- Nombre comercial.
- Descripción.
- Categoría.
- Subcategoría.
- Marca del repuesto.
- Referencia del fabricante.
- Número OEM opcional.
- Compatibilidad con vehículos.
- Unidad de medida.
- Costo de referencia calculado.
- Precio de venta.
- Porcentaje de margen estimado.
- Stock mínimo.
- Estado activo/inactivo.
- Imágenes.
- Fecha de creación y actualización.

Ejemplos de categorías: amortiguadores, frenos, suspensión, dirección, filtros, motor, transmisión y sistema eléctrico.

Permitir:

- Crear, consultar, editar y desactivar productos.
- Buscar por SKU, nombre, referencia, marca o código OEM.
- Filtrar por categoría, vehículo o disponibilidad.
- Importar productos desde Excel o CSV con validación y vista previa.
- Exportar el catálogo.
- Registrar múltiples imágenes.
- Identificar productos duplicados antes de crearlos.
- Registrar referencias equivalentes sin asumir compatibilidad automáticamente.

### 5. Módulo de vehículos y compatibilidad

Un mismo repuesto puede servir para diferentes vehículos.

Crear catálogos de:

- Fabricantes de vehículos.
- Modelos.
- Versiones.
- Años o rangos de años.
- Motorización opcional.
- Observaciones de compatibilidad.

Establecer una relación muchos a muchos entre productos y aplicaciones vehiculares.

Ejemplo: un amortiguador puede tener distintas aplicaciones, siempre que esa compatibilidad haya sido verificada.

Permitir buscar los repuestos disponibles para un vehículo específico.

No inventar compatibilidades mecánicas.

### 6. Módulo de proveedores — Prioridad alta

Este es uno de los módulos más importantes del negocio.

Cada proveedor debe tener:

- ID.
- Nombre comercial o razón social.
- NIT o identificación.
- Persona de contacto.
- Teléfono y WhatsApp.
- Correo electrónico.
- Ciudad.
- Dirección.
- Condiciones de pago.
- Plazo habitual de entrega.
- Observaciones.
- Estado activo/inactivo.

**Catálogo individual de cada proveedor**

Implementar una relación muchos a muchos entre productos y proveedores.

Cada registro de oferta debe contener:

- ID del proveedor.
- ID del producto interno.
- Código o referencia utilizada por ese proveedor.
- Precio de compra en COP.
- Moneda, inicialmente COP.
- Cantidad mínima de compra.
- Descuentos aplicables.
- Tiempo estimado de entrega.
- Vigencia del precio.
- Disponibilidad informada.
- Garantía.
- Fecha de última actualización.

Un proveedor puede comercializar miles de repuestos y un producto puede aparecer en múltiples catálogos.

**Comparador de proveedores**

Al consultar cualquier repuesto, mostrar:

| Proveedor | Precio compra | Entrega | Disponibilidad |
|---|---:|---|---|
| Proveedor A | $85.000 | 2 días | Disponible |
| Proveedor B | $79.000 | 5 días | Por confirmar |
| Proveedor C | $92.000 | 1 día | Disponible |

Los valores son únicamente datos ilustrativos.

Permitir:

- Ordenar por precio.
- Comparar costos adicionales y costo total de adquisición.
- Comparar tiempos de entrega.
- Consultar el historial de precios.
- Identificar la oferta más económica vigente.
- Identificar ofertas vencidas.
- Cargar y actualizar catálogos masivos mediante Excel/CSV.
- Generar una propuesta de compra por proveedor.

El precio más bajo no siempre debe considerarse la mejor oferta: mostrar también entrega, confiabilidad y condiciones.

La disponibilidad del proveedor no debe confundirse con el inventario propio.

### 7. Módulo de inventario

Implementar un sistema de inventario basado en movimientos trazables.

No limitarse a actualizar un campo `stock`.

Gestionar:

- Bodegas y ubicaciones físicas.
- Existencias por producto y bodega.
- Stock disponible.
- Stock reservado.
- Stock mínimo.
- Entradas por compras recibidas.
- Salidas por ventas entregadas.
- Devoluciones.
- Ajustes por pérdida, daño o diferencias.
- Traslados entre bodegas.
- Historial de movimientos.
- Alertas de inventario bajo.

Cada movimiento debe registrar:

- Producto.
- Bodega origen y/o destino.
- Tipo de movimiento.
- Cantidad.
- Fecha.
- Usuario responsable.
- Documento relacionado.
- Motivo.
- Costo asociado cuando corresponda.

**Reglas fundamentales**

- Impedir inventario negativo por defecto.
- Los movimientos confirmados no deben eliminarse ni editarse directamente.
- Corregir errores mediante movimientos compensatorios.
- Evitar registrar dos veces un mismo movimiento por reintentos.
- Manejar concurrencia mediante transacciones y bloqueos apropiados.
- Mantener consistencia entre existencias y movimientos.
- No permitir que productos desactivados desaparezcan del historial.

El sistema debe poder responder exactamente cómo se llegó a una existencia determinada.

### 8. Módulo de compras

Crear un flujo completo:

**Borrador → Orden emitida → Recepción parcial o total → Cierre.**

Debe permitir:

- Seleccionar proveedor.
- Agregar múltiples repuestos.
- Consultar y seleccionar ofertas.
- Registrar cantidades.
- Aplicar descuentos.
- Registrar transporte y costos adicionales.
- Calcular total de compra.
- Registrar número de factura del proveedor.
- Registrar anticipos y pagos.
- Crear órdenes de compra en PDF.
- Recibir mercancía parcialmente.
- Actualizar inventario únicamente cuando se confirma la recepción.
- Asociar costos de adquisición a las unidades recibidas.
- Registrar devoluciones al proveedor.

No modificar el costo histórico de mercancía previamente adquirida cuando cambie el precio del proveedor.

### 9. Módulo de ventas

Crear una interfaz sencilla y rápida de ventas.

Funcionalidades:

- Buscar productos.
- Consultar stock disponible.
- Agregar productos a una venta.
- Establecer cantidades.
- Aplicar descuentos autorizados.
- Calcular subtotal y total.
- Registrar clientes opcionalmente.
- Registrar método de pago.
- Generar comprobante interno en PDF.
- Consultar historial.
- Anular o devolver ventas mediante operaciones controladas.
- Actualizar inventario en el momento definido para la entrega.
- Calcular costo y utilidad estimada por venta.

Métodos iniciales: efectivo, transferencia, Nequi, Daviplata y otros configurables.

Separar los estados de pago, venta y entrega.

Evitar descontar existencias dos veces o confirmar ventas con cantidades superiores a la disponibilidad.

Los comprobantes internos no deben presentarse como facturación electrónica DIAN. Preparar la arquitectura para integrarla posteriormente.

### 10. Módulo financiero y rentabilidad

Este módulo debe ayudar a determinar si el negocio realmente está generando ganancias.

**Indicadores**
- Valor del inventario al costo.
- Total de compras.
- Total de ventas.
- Costo de mercancía vendida.
- Utilidad bruta.
- Margen bruto.
- Gastos operativos registrados.
- Resultado operativo estimado.
- Cuentas pendientes de proveedores.
- Ventas pendientes de cobro.
- Productos más rentables.
- Capital invertido en inventario.

Utilizar inicialmente **costo promedio ponderado móvil**, implementado con una política de valoración consistente y documentada.

Distinguir claramente margen y recargo sobre costo.

Fórmulas:

Margen bruto = (Venta neta - Costo de mercancía vendida) / Venta neta × 100.

Recargo sobre costo = (Venta neta - Costo) / Costo × 100.

Implementar tratamiento adecuado de valores nulos, devoluciones y descuentos.

Usar `decimal.Decimal` en Python y `NUMERIC` en PostgreSQL para dinero. No utilizar `float` ni `double` para cálculos monetarios.

**Socios**

El negocio inicialmente tendrá dos socios, con participación prevista del 50 % cada uno.

Registrar:

- Socios.
- Porcentajes de participación.
- Aportes de capital.
- Retiros.
- Distribuciones de utilidades.
- Historial de movimientos de capital.

Las aportaciones no son ingresos por ventas, y los retiros no deben registrarse automáticamente como gastos del negocio.

No implementar una contabilidad tributaria completa en esta primera etapa.

### 11. Módulo de dashboard

Crear un panel de inicio moderno con:

- Ventas del día y del mes.
- Utilidad bruta estimada del mes.
- Valor del inventario.
- Número de productos activos.
- Productos con stock bajo.
- Productos agotados.
- Compras pendientes.
- Productos más vendidos.
- Evolución mensual de ventas.
- Rotación de inventario.

Agregar filtros de fechas, estados y bodegas.

Las gráficas deben consumir datos reales de la API.

### 12. Alertas y recomendaciones

Implementar alertas para:

- Stock por debajo del mínimo.
- Productos agotados.
- Órdenes de compra pendientes.
- Productos sin movimiento durante determinado periodo.
- Precios de proveedores desactualizados.
- Productos cuyo precio de venta no cubre su costo estimado.

Preparar una recomendación básica de reposición basada en ventas históricas, stock y tiempo de entrega.

No agregar inteligencia artificial compleja en el MVP. Priorizar reglas deterministas, explicables y verificables.

### 13. Diseño de interfaz

Quiero una aplicación visualmente moderna y profesional, similar a un SaaS comercial.

Características:

- Dashboard principal.
- Menú lateral de navegación.
- Diseño responsive para escritorio, tablet y celular.
- Tablas con búsqueda, filtros, ordenación y paginación.
- Formularios claros.
- Indicadores de carga.
- Mensajes de error comprensibles.
- Confirmaciones antes de operaciones sensibles.
- Estados vacíos útiles.
- Accesibilidad básica.
- Consistencia visual.
- Diseño limpio sin elementos decorativos innecesarios.

El sistema debe estar en español.

Usar formato monetario colombiano y zona horaria `America/Bogota`, almacenando los instantes de forma consistente.

### 14. Modelo de datos

Diseñar un esquema relacional PostgreSQL normalizado, con claves primarias, foráneas, índices, restricciones y reglas de integridad.

Considerar, como mínimo, estas entidades o sus equivalentes:

**Seguridad**
- users
- roles
- permissions
- user_roles
- role_permissions
- audit_logs

**Catálogos**
- products
- product_categories
- brands
- product_images
- vehicle_makes
- vehicle_models
- vehicle_versions
- product_vehicle_applications

**Proveedores**
- suppliers
- supplier_products
- supplier_price_history

**Inventario**
- warehouses
- warehouse_locations
- inventory_balances
- inventory_movements
- inventory_adjustments
- inventory_reservations

**Compras**
- purchase_orders
- purchase_order_items
- purchase_receipts
- purchase_receipt_items
- supplier_payments

**Ventas**
- customers
- sales
- sale_items
- sale_payments
- sale_returns

**Finanzas**
- business_expenses
- partners
- capital_movements
- profit_distributions

Puedes agregar o reorganizar tablas si mejoras la integridad del modelo.

No crees columnas redundantes sin justificarlo.

Utiliza UUID cuando resulte conveniente, `NUMERIC` para valores monetarios y cantidades con la precisión requerida, claves únicas para SKU y referencias según su ámbito, y fechas de auditoría.

Todas las modificaciones estructurales deben ejecutarse mediante migraciones Alembic versionadas.

### 15. Arquitectura backend

Organizar el backend por módulos de negocio y separar claramente:

- Rutas HTTP FastAPI.
- Esquemas Pydantic v2 de entrada y salida.
- Casos de uso o servicios de aplicación.
- Entidades de dominio.
- Repositorios.
- Validaciones.
- Manejo centralizado de excepciones.
- Seguridad.
- Configuración.
- Integraciones e infraestructura.

No exponer directamente modelos SQLAlchemy como contratos públicos.

Implementar:

- Respuestas HTTP apropiadas.
- Manejo uniforme de errores con códigos identificables.
- Paginación.
- Filtros.
- Validación de entradas.
- OpenAPI.
- Transacciones en operaciones críticas.
- Idempotencia en confirmaciones sensibles.
- Logging estructurado sin exponer datos secretos.
- CORS restringido.
- Protección de credenciales.
- Control de acceso por permisos.
- Migraciones reproducibles.

No usar `create_all()` para evolucionar esquemas en producción; utilizar Alembic.

### 16. Calidad y pruebas

Implementar:

- Pruebas unitarias de reglas de negocio.
- Pruebas de integración con PostgreSQL mediante Testcontainers cuando sea viable.
- Pruebas de endpoints.
- Pruebas de autorización por roles.
- Pruebas de cálculos monetarios.
- Pruebas de ventas simultáneas.
- Pruebas de recepción parcial.
- Pruebas de devoluciones.
- Pruebas de integridad de inventario.
- Pruebas básicas de frontend.

Escenarios obligatorios:

1. Registrar un producto con varios proveedores.
2. Comparar sus precios.
3. Crear una orden de compra.
4. Recibir mercancía parcialmente.
5. Verificar el aumento correcto del stock.
6. Registrar una venta.
7. Verificar que el stock disminuyó.
8. Calcular correctamente costo y utilidad.
9. Rechazar una venta sin existencias suficientes.
10. Devolver una venta y generar el movimiento correspondiente.
11. Comprobar que un vendedor sin permiso no puede consultar los costos.
12. Verificar que repetir la confirmación de recepción no duplica existencias.

### 17. Documentación universitaria

Crear una carpeta `/docs` que contenga:

- Descripción del problema.
- Justificación.
- Objetivo general.
- Objetivos específicos.
- Alcance funcional.
- Requisitos funcionales y no funcionales.
- Historias de usuario.
- Casos de uso.
- Diagrama de arquitectura.
- Diagrama entidad-relación.
- Diagramas de componentes.
- Diagramas de secuencia para compras y ventas.
- Modelo C4, al menos contexto y contenedores.
- Decisiones arquitectónicas ADR.
- Matriz de pruebas.
- Manual técnico.
- Manual de usuario.
- Instrucciones de instalación.

Utilizar Mermaid o PlantUML para diagramas mantenibles como código.

La documentación debe reflejar el software realmente implementado, no funcionalidades inexistentes.

### 18. Estrategia de desarrollo por fases

El proyecto debe construirse incrementalmente.

**Fase 1 — Fundamentos**
- Estructura del repositorio.
- Backend inicial.
- Frontend inicial.
- PostgreSQL.
- Docker Compose.
- Migraciones.
- Autenticación.
- Usuarios y roles.

**Fase 2 — Catálogos**
- Categorías.
- Marcas.
- Productos.
- Vehículos y compatibilidad básica.
- Búsquedas y filtros.

**Fase 3 — Proveedores**
- CRUD de proveedores.
- Catálogos por proveedor.
- Comparador de precios.
- Historial de precios.
- Importación masiva.

**Fase 4 — Inventario y compras**
- Bodegas.
- Movimientos.
- Existencias.
- Órdenes de compra.
- Recepciones.
- Valoración de inventario.

**Fase 5 — Ventas**
- Clientes.
- Ventas.
- Pagos.
- Devoluciones.
- Comprobantes PDF.

**Fase 6 — Finanzas**
- Utilidad.
- Gastos.
- Aportes de socios.
- Dashboard.
- Reportes.

**Fase 7 — Calidad y preparación**
- Pruebas completas.
- Seguridad.
- Documentación universitaria.
- Datos iniciales.
- Guía de despliegue.
- Respaldo y restauración.
- Revisión final.

No intentes implementar todas las fases en una sola respuesta ni mezclar funcionalidades incompletas.

### 19. Reglas de trabajo para Codex

1. Inspecciona el repositorio antes de crear o modificar archivos.
2. Si está vacío, inicializa la estructura completa.
3. No me pidas crear manualmente archivos que puedas generar.
4. Construye software real, no pseudocódigo.
5. No utilices respuestas simuladas para funcionalidades que deban consultar la base de datos.
6. No dejes métodos vacíos ni TODOs dentro del alcance de una fase que declares terminada.
7. Ejecuta compilaciones, migraciones y pruebas cuando el entorno lo permita.
8. Si algo falla, identifica la causa y corrígela.
9. No elimines código funcional sin justificarlo.
10. Mantén consistencia entre frontend, API y base de datos.
11. Documenta las decisiones técnicas importantes.
12. Utiliza datos de demostración claramente identificados, distintos de los datos reales.
13. Nunca almacenes credenciales reales en el repositorio.
14. Mantén un registro del avance por fases y funcionalidades pendientes.
15. Cuando falte un requisito secundario, toma una decisión razonable y documéntala; consulta únicamente decisiones que cambien significativamente el negocio.
16. Al terminar cada fase, entrega un resumen de archivos, funcionalidades, pruebas ejecutadas y pasos de validación.

### 20. Resultado esperado

Al finalizar el proyecto debe existir un repositorio con:

- Aplicación web funcional.
- Backend REST.
- Base de datos PostgreSQL.
- Migraciones.
- Seguridad y roles.
- Módulos operativos integrados.
- Pruebas automatizadas.
- Documentación técnica y académica.
- Instrucciones claras de ejecución.
- Configuración de desarrollo reproducible con Docker Compose.
- Arquitectura preparada para una futura aplicación móvil.

### 21. Primera instrucción de ejecución

Comienza ahora con la **Fase 1**.

Primero define y documenta brevemente la arquitectura y la estructura de carpetas. Después crea los proyectos reales del backend y frontend, configura PostgreSQL, Docker Compose, Alembic y el sistema de autenticación.

Crea la primera migración, los endpoints necesarios, las pantallas de inicio de sesión y una vista principal protegida.

Incluye una estrategia segura de creación del primer administrador, sin credenciales predeterminadas inseguras.

Verifica que los componentes se comuniquen correctamente y que los proyectos compilen.

No avances a la Fase 2 hasta comprobar los criterios de aceptación de la Fase 1.

**Prioridad absoluta: código funcional, mantenible, seguro y aprovechable para el negocio real.**