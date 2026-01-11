# Backlog

## Linea de tiempo y analisis por hora
- Generar una linea de tiempo que avance por bloques horarios (09:00, 10:00, 11:00, etc.) y cree un punto por cada hora procesada.
- El proceso debe correr solo al llegar a cada hora en punto; entre 08:50 y 08:59 no pasa nada, a las 09:00 se ejecuta una vez, lee todos los ingresos y movimientos hasta las 09:00 y actualiza el dashboard.
- Repetir en 10:00, 11:00, 12:00, etc., refrescando el dashboard con los ingresos/egresos acumulados hasta esa hora.
- La visualizacion debe mostrar la progresion hora por hora hasta la hora objetivo (ejemplo: llegar a 14:00 mostrando 09:00, 10:00, 11:00, 12:00, 13:00, 14:00).
- Permitir al administrador ver en que horas hubo picos de entrada/salida y en que horas casi no hubo movimiento.
