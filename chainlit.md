# Asistente IA con Memoria Persistente 🤖💾

¡Bienvenido! Este es un asistente de IA potenciado por **LangGraph** con memoria persistente y autenticación de usuarios.

## 🌟 Características

- **Memoria Persistente**: Todas tus conversaciones se guardan automáticamente en una base de datos SQLite local
- **Autenticación de Usuarios**: Cada usuario tiene su propio historial de conversación privado
- **Búsqueda Web**: El asistente puede buscar información actualizada en internet usando Tavily
- **Conversaciones Privadas**: Tu historial es completamente privado y está separado de otros usuarios

## 👤 Usuarios de Prueba

Para esta demostración, puedes iniciar sesión con cualquiera de estos usuarios:

- **admin** / admin123 (Administrador)
- **maria** / guapo123 (Mikel Garcia)
- **juan** / fe123 (Juan Pérez)

## 💡 Cómo Usar

1. **Inicia sesión** con uno de los usuarios de prueba
2. **Chatea** con el asistente normalmente
3. **Pregúntale tu nombre** después de decírselo - verás que lo recuerda
4. **Cierra sesión y vuelve a entrar** - tu conversación seguirá ahí
5. **Prueba con otro usuario** - cada usuario tiene su propia conversación separada

## 🔒 Seguridad

⚠️ **Nota**: Esta es una implementación de demostración. En producción, las contraseñas deben estar hasheadas y los usuarios deben almacenarse en una base de datos segura.

## 📚 Recursos

- **Documentación de Chainlit**: [docs.chainlit.io](https://docs.chainlit.io)
- **LangGraph**: [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph)

¡Disfruta conversando con tu asistente personal! 🎉
