"""Seguridad, sesiones, RBAC y auditoría; sin usuarios ni credenciales iniciales."""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0001_identity"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "permissions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(80), nullable=False, unique=True),
        sa.Column("description", sa.String(200), nullable=False),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(40), nullable=False, unique=True),
        sa.Column("name", sa.String(80), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("failed_attempts >= 0", name="failed_attempts_nonnegative"),
    )
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "role_id", sa.Uuid(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
        ),
    )
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id", sa.Uuid(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "permission_id",
            sa.Uuid(),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("user_agent", sa.String(256), nullable=False),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("auth_sessions.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_refresh_tokens_session_id", "refresh_tokens", ["session_id"])
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("target_id", sa.String(80)),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    for column in ["actor_id", "action", "created_at"]:
        op.create_index(f"ix_audit_logs_{column}", "audit_logs", [column])

    # Seeds versionados, nunca importados desde código mutable de aplicación.
    descriptions = {
        "users.manage": "Administrar usuarios y asignar roles",
        "catalog.read": "Consultar catálogo y disponibilidad",
        "catalog.manage": "Administrar productos y aplicaciones verificadas",
        "suppliers.manage": "Administrar proveedores y ofertas",
        "costs.read": "Consultar costos internos",
        "inventory.read": "Consultar inventario propio",
        "inventory.manage": "Registrar movimientos y ajustes",
        "purchases.manage": "Administrar compras y recepciones",
        "customers.manage": "Administrar clientes",
        "sales.manage": "Registrar ventas y devoluciones",
        "finance.read": "Consultar rentabilidad y reportes",
        "finance.manage": "Administrar gastos y capital",
    }
    role_grants = {
        "admin": ("Administrador", list(descriptions)),
        "partner": (
            "Socio",
            [
                "catalog.read",
                "suppliers.manage",
                "costs.read",
                "inventory.read",
                "purchases.manage",
                "sales.manage",
                "customers.manage",
                "finance.read",
            ],
        ),
        "seller": (
            "Vendedor",
            ["catalog.read", "inventory.read", "customers.manage", "sales.manage"],
        ),
        "inventory": (
            "Inventario",
            ["catalog.read", "catalog.manage", "inventory.read", "inventory.manage"],
        ),
    }
    permissions = {code: uuid4() for code in descriptions}
    permission_table = sa.table(
        "permissions", sa.column("id", sa.Uuid()), sa.column("code"), sa.column("description")
    )
    role_table = sa.table("roles", sa.column("id", sa.Uuid()), sa.column("code"), sa.column("name"))
    grants_table = sa.table(
        "role_permissions", sa.column("role_id", sa.Uuid()), sa.column("permission_id", sa.Uuid())
    )
    op.bulk_insert(
        permission_table,
        [{"id": permissions[c], "code": c, "description": d} for c, d in descriptions.items()],
    )
    for code, (name, grants) in role_grants.items():
        role_id = uuid4()
        op.bulk_insert(role_table, [{"id": role_id, "code": code, "name": name}])
        op.bulk_insert(
            grants_table, [{"role_id": role_id, "permission_id": permissions[p]} for p in grants]
        )


def downgrade():
    for table in [
        "audit_logs",
        "refresh_tokens",
        "auth_sessions",
        "role_permissions",
        "user_roles",
        "users",
        "roles",
        "permissions",
    ]:
        op.drop_table(table)
