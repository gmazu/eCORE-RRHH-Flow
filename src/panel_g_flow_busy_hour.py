from manim import *
import os
import sys
from pathlib import Path
from datetime import datetime
import random
import numpy as np
import yaml

# Agregar src/ al path
sys.path.insert(0, str(Path(__file__).parent))
from loader import SistemaDistribucion


class PanelG_FlowBusyHour(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a1a"

        fecha = os.environ.get("R2H2_FECHA")
        if fecha:
            path_eventos = f"data/{fecha}"
        else:
            path_eventos = "data"

        try:
            sistema = SistemaDistribucion(
                path_eventos=path_eventos,
                path_config="config/configuracion.yaml"
            )
        except Exception as e:
            self.mostrar_error(f"Error al cargar datos: {e}")
            return

        eventos = sistema.eventos
        asignaciones = sistema.asignaciones

        # ========================================
        # CONFIG VELOCIDADES (desde config/configuracion.yaml)
        # ========================================
        vel_cfg = sistema.config.get("velocidades", {})

        # Timeline
        timeline_slide_seconds = float(vel_cfg.get("timeline_slide", 0.4))

        # Velocidades (mayor = más rápido)
        velocidad_entrada = float(vel_cfg.get("entrada", 1.0))
        velocidad_escalera = float(vel_cfg.get("escalera", 1.0))
        velocidad_salida = float(vel_cfg.get("salida", 1.0))
        velocidad_interno = float(vel_cfg.get("interno", 1.0))
        wave_duration_max = float(vel_cfg.get("wave_duration_max", 6.0))

        # Tiempos base (internos, no configurables)
        base_entrada = 1.2
        base_escalera = 0.8
        base_salida = 0.9
        base_interno = 0.7

        # Variación individual y micro-pausas
        velocidad_min = float(vel_cfg.get("variacion_min", 0.7))
        velocidad_max = float(vel_cfg.get("variacion_max", 1.4))
        micro_pausa_prob = float(vel_cfg.get("micro_pausa_prob", 0.3))
        micro_pausa_min = float(vel_cfg.get("micro_pausa_min", 0.1))
        micro_pausa_max = float(vel_cfg.get("micro_pausa_max", 0.4))

        # ========================================
        # TITULO
        # ========================================
        titulo = Text("FLOW BUSY HOUR", font_size=34, color=WHITE)
        subtitulo = Text("Linea de tiempo por hora • Movimiento por piso", font_size=18, color=GRAY)
        titulo.to_edge(UP, buff=0.4)
        subtitulo.next_to(titulo, DOWN, buff=0.2)
        self.play(Write(titulo), Write(subtitulo))

        # ========================================
        # MAPEO DE PERSONAS Y ZONAS
        # ========================================
        depto_por_id = {}
        for depto, ids in asignaciones.items():
            for tarjeta in ids:
                depto_por_id[tarjeta] = depto

        ids_eventos = {e["id_tarjeta"] for e in eventos}
        ids_definidos = set(depto_por_id.keys())
        ids_totales = sorted(ids_definidos | ids_eventos)

        presentes_hoy = {e["id_tarjeta"] for e in eventos if e.get("id_tarjeta") in ids_definidos}
        total_personas = len(ids_definidos)
        asistencia_pct = (len(presentes_hoy) / max(total_personas, 1)) * 100

        # ========================================
        # ESCENA DEL EDIFICIO
        # ========================================
        building_center_x = 2.5
        building_width = 6.0
        floor_height = 0.9
        building_bottom = -1.6

        floor_centers = [
            building_bottom + floor_height * 0.5,
            building_bottom + floor_height * 1.5,
            building_bottom + floor_height * 2.5,
            building_bottom + floor_height * 3.5,
        ]
        floor_surface_y = [y - floor_height / 2 + 0.08 for y in floor_centers]

        building = Rectangle(
            width=building_width,
            height=floor_height * 4,
            stroke_color=WHITE,
            stroke_width=2
        ).move_to([building_center_x, building_bottom + floor_height * 2, 0])

        pisos = VGroup()
        for i, y in enumerate(floor_centers, start=1):
            piso = Rectangle(
                width=building_width,
                height=floor_height,
                stroke_color=GRAY,
                stroke_width=1.5
            ).move_to([building_center_x, y, 0])
            pisos.add(piso)

        labels = VGroup(
            Text("PISO 1 • ENTRADA", font_size=14, color=GRAY).move_to([building_center_x, floor_centers[0], 0]),
            Text("PISO 2 • DEPTO A", font_size=14, color="#4A90E2").move_to([building_center_x, floor_centers[1], 0]),
            Text("PISO 3 • DEPTO B / C", font_size=14, color=WHITE).move_to([building_center_x, floor_centers[2], 0]),
            Text("PISO 4 • CASINO", font_size=14, color="#F39C12").move_to([building_center_x, floor_centers[3], 0]),
        )

        split_line = Line(
            [building_center_x, floor_centers[2] - floor_height / 2, 0],
            [building_center_x, floor_centers[2] + floor_height / 2, 0],
            color=GRAY
        )

        self.play(Create(building), Create(pisos), FadeIn(labels), Create(split_line))

        # Elevador (visual)
        elevator_x = building_center_x + building_width / 2 - 0.45
        elevator_shaft = Rectangle(
            width=0.7,
            height=floor_height * 4,
            stroke_color=GRAY,
            stroke_width=1.5
        ).move_to([elevator_x, building_bottom + floor_height * 2, 0])

        cab_width = 0.55
        cab_height = 0.55
        elevator_cab = Rectangle(
            width=cab_width,
            height=cab_height,
            fill_color="#2B2B2B",
            fill_opacity=1.0,
            stroke_color=WHITE,
            stroke_width=1.5
        ).move_to([elevator_x, floor_centers[0], 0])

        door_left = Rectangle(
            width=cab_width * 0.45,
            height=cab_height * 0.9,
            fill_color="#1A1A1A",
            fill_opacity=1.0,
            stroke_color=GRAY,
            stroke_width=1.0
        ).move_to(elevator_cab.get_center() + LEFT * (cab_width * 0.15))
        door_right = door_left.copy().move_to(elevator_cab.get_center() + RIGHT * (cab_width * 0.15))
        elevator_doors = VGroup(door_left, door_right)
        elevator = VGroup(elevator_cab, elevator_doors)

        self.play(Create(elevator_shaft), FadeIn(elevator))

        # Escaleras (visual)
        stairs_x = elevator_x - 0.9
        stairs = Rectangle(
            width=0.5,
            height=floor_height * 4,
            stroke_color=GRAY,
            stroke_width=1.2
        ).move_to([stairs_x, building_bottom + floor_height * 2, 0])
        stairs_label = Text("ESC.", font_size=10, color=GRAY)
        stairs_label.next_to(stairs, UP, buff=0.05)
        self.play(Create(stairs), FadeIn(stairs_label))

        # ========================================
        # ZONAS Y POSICIONES
        # ========================================
        zonas = {
            "fuera": (-9.0, -7.2),
            "lobby": (building_center_x - 2.8, building_center_x + 2.8),
            "depto_a": (building_center_x - 2.8, building_center_x + 2.8),
            "depto_b": (building_center_x - 2.8, building_center_x - 0.2),
            "depto_c": (building_center_x + 0.2, building_center_x + 2.8),
            "casino": (building_center_x - 2.8, building_center_x + 2.8),
        }

        zone_y = {
            "fuera": floor_surface_y[0],
            "lobby": floor_surface_y[0],
            "depto_a": floor_surface_y[1],
            "depto_b": floor_surface_y[2],
            "depto_c": floor_surface_y[2],
            "casino": floor_surface_y[3],
        }

        piso_extendido = Line(
            np.array([-7.6, floor_surface_y[0], 0]),
            np.array([building_center_x + building_width / 2, floor_surface_y[0], 0]),
            color=GRAY,
            stroke_width=2
        )
        self.play(Create(piso_extendido))

        # Contadores de ocupación actual
        ocupacion_dentro = 0
        contador_in = Text("Dentro: 0", font_size=20, color="#50C878")
        contador_out = Text("Fuera: 100", font_size=20, color="#E74C3C")
        total_text = Text(f"Personas: {total_personas}", font_size=18, color=WHITE)
        asistencia_text = Text(f"Asistencia: {asistencia_pct:.1f}%", font_size=18, color=WHITE)
        contador_in.to_corner(UR, buff=0.6)
        contador_out.next_to(contador_in, DOWN, buff=0.2, aligned_edge=RIGHT)
        total_text.next_to(contador_out, DOWN, buff=0.2, aligned_edge=RIGHT)
        asistencia_text.next_to(total_text, DOWN, buff=0.2, aligned_edge=RIGHT)
        self.play(FadeIn(contador_in), FadeIn(contador_out), FadeIn(total_text), FadeIn(asistencia_text))

        def pos_random(tarjeta: str, zona: str) -> list:
            xmin, xmax = zonas[zona]
            seed = f"{tarjeta}:{zona}"
            rng = random.Random(seed)
            return [rng.uniform(xmin, xmax), zone_y[zona], 0]

        # ========================================
        # CREAR PERSONAS
        # ========================================
        dots = {}
        dot_group = VGroup()

        for tarjeta in ids_totales:
            depto = depto_por_id.get(tarjeta)
            if depto == "DEPTO_A":
                color = "#4A90E2"
            elif depto == "DEPTO_B":
                color = "#50C878"
            elif depto == "DEPTO_C":
                color = "#9B59B6"
            else:
                color = GRAY

            dot = Dot(point=pos_random(tarjeta, "fuera"), radius=0.05, color=color)
            dots[tarjeta] = dot
            dot_group.add(dot)

        self.play(FadeIn(dot_group), run_time=1.0)

        # ========================================
        # LINEA DE TIEMPO
        # ========================================
        timeline_y = -3.2
        timeline = Line(LEFT * 6, RIGHT * 6, color=GRAY)
        timeline.move_to([0, timeline_y, 0])

        puntos = VGroup()
        for i in range(24):
            x = -6 + i * (12 / 23)
            punto = Dot(point=[x, timeline_y, 0], radius=0.04, color=GRAY)
            puntos.add(punto)

        labels_hora = VGroup()
        for i in range(0, 24, 3):
            x = -6 + i * (12 / 23)
            label = Text(f"{i:02d}", font_size=10, color=GRAY)
            label.move_to([x, timeline_y - 0.25, 0])
            labels_hora.add(label)

        marcador = Dot(point=puntos[0].get_center(), radius=0.08, color="#F39C12")
        hora_text = Text("00:00", font_size=16, color=WHITE)
        hora_text.next_to(timeline, UP, buff=0.2)

        self.play(Create(timeline), FadeIn(puntos), FadeIn(labels_hora), FadeIn(marcador), FadeIn(hora_text))

        # ========================================
        # PROCESAR EVENTOS POR HORA
        # ========================================
        eventos_por_hora = {h: [] for h in range(24)}
        for evento in eventos:
            try:
                ts = datetime.fromisoformat(evento["timestamp"])
            except ValueError:
                continue
            eventos_por_hora[ts.hour].append((ts, evento))

        estado = {tarjeta: "fuera" for tarjeta in ids_totales}
        zona_actual = {tarjeta: "fuera" for tarjeta in ids_totales}

        def mover_por_escalera(dot, destino, run_time=0.3):
            start = dot.get_center()
            if np.allclose(start, destino):
                return None
            p1 = np.array([stairs_x, floor_surface_y[0], 0])
            p2 = np.array([stairs_x, destino[1], 0])
            path = VMobject()
            path.set_points_as_corners([start, p1, p2, destino])
            # smooth para movimiento orgánico (acelera y desacelera)
            return MoveAlongPath(dot, path, rate_func=smooth, run_time=run_time)

        def mover_lineal(dot, destino, run_time=0.3):
            start = dot.get_center()
            if np.allclose(start, destino):
                return None
            path = Line(start, destino)
            # smooth para que no se vea robótico
            return MoveAlongPath(dot, path, rate_func=smooth, run_time=run_time)

        def gaussian_delays(count: int, total_duration: float, seed: str) -> list:
            """Genera delays gaussianos para simular llegada tipo 'ola de hormigas'."""
            if count <= 1:
                return [0.0] * count
            rng = random.Random(seed)
            # Distribución gaussiana más pronunciada para efecto de ola
            samples = [rng.gauss(0.5, 0.25) for _ in range(count)]
            # Clamp entre 0 y 1
            samples = [max(0.0, min(1.0, s)) for s in samples]
            return [s * total_duration for s in samples]

        def velocidad_hormiga(seed: str) -> float:
            """Cada hormiga tiene su propia velocidad - algunas rápidas, otras lentas."""
            rng = random.Random(seed)
            return rng.uniform(velocidad_min, velocidad_max)

        def micro_pausa(seed: str) -> float:
            """Micro-pausas aleatorias como si conversaran o se cruzaran."""
            rng = random.Random(seed)
            if rng.random() < micro_pausa_prob:
                return rng.uniform(micro_pausa_min, micro_pausa_max)
            return 0.0

        def aplicar_evento(evento: dict) -> None:
            tarjeta = evento["id_tarjeta"]
            puerta = evento["puerta"]
            tipo = evento["tipo"]

            if puerta in (1, 2, 3) and tipo == "entrada":
                depto = depto_por_id.get(tarjeta)
                if depto == "DEPTO_A":
                    estado[tarjeta] = "depto_a"
                elif depto == "DEPTO_B":
                    estado[tarjeta] = "depto_b"
                elif depto == "DEPTO_C":
                    estado[tarjeta] = "depto_c"
                else:
                    estado[tarjeta] = "lobby"
            elif puerta == 6 and tipo == "entrada":
                depto = depto_por_id.get(tarjeta)
                if depto == "DEPTO_A":
                    estado[tarjeta] = "depto_a"
                elif depto == "DEPTO_B":
                    estado[tarjeta] = "depto_b"
                elif depto == "DEPTO_C":
                    estado[tarjeta] = "depto_c"
                else:
                    estado[tarjeta] = "lobby"
            elif puerta == 5:
                estado[tarjeta] = "casino"
            elif puerta == 7:
                estado[tarjeta] = "lobby"
            elif puerta == 4:
                estado[tarjeta] = "fuera"
            elif tipo == "salida":
                estado[tarjeta] = "fuera"

        # ========================================
        # ANIMAR POR HORA
        # ========================================
        prev_marker_pos = marcador.get_center().copy()
        for hora in range(24):
            eventos_hora = sorted(eventos_por_hora[hora], key=lambda x: x[0])
            for _, evento in eventos_hora:
                aplicar_evento(evento)

            # Contar ocupación actual (personas dentro del edificio)
            ocupacion_dentro = sum(1 for t in ids_totales if estado[t] != "fuera")
            ocupacion_fuera = total_personas - ocupacion_dentro

            movimientos = []
            for tarjeta, dot in dots.items():
                actual = zona_actual[tarjeta]
                objetivo = estado[tarjeta]
                if actual != objetivo:
                    movimientos.append((tarjeta, actual, objetivo))
            movimientos.sort(key=lambda item: dots[item[0]].get_center()[0])
            entrando = [(t, a, o) for t, a, o in movimientos if a == "fuera" and o != "fuera"]
            saliendo = [(t, a, o) for t, a, o in movimientos if a != "fuera" and o == "fuera"]
            internos = [(t, a, o) for t, a, o in movimientos if t not in {m[0] for m in entrando + saliendo}]

            # Agrupar entrantes por departamento (campana gaussiana independiente por color)
            entrando_por_depto = {}
            for t, a, o in entrando:
                depto = depto_por_id.get(t, "OTROS")
                if depto not in entrando_por_depto:
                    entrando_por_depto[depto] = []
                entrando_por_depto[depto].append((t, a, o))

            # Orden cromático: azul (DEPTO_A) → verde (DEPTO_B) → morado (DEPTO_C) → otros
            orden_colores = ["DEPTO_A", "DEPTO_B", "DEPTO_C", "OTROS"]

            # Duración base de ola (para salidas/internos si no hay entradas)
            wave_duration = wave_duration_max

            # Animar cada grupo en orden cromático (secuencial)
            # Primero entran al lobby, luego suben - todo por color
            for depto in orden_colores:
                if depto not in entrando_por_depto:
                    continue
                grupo = entrando_por_depto[depto]
                if not grupo:
                    continue

                # FASE 1: Entrar al lobby (campana gaussiana)
                wave_in = []
                wave_duration = min(wave_duration_max, max(1.5, 1.0 + 0.12 * len(grupo)))
                delays = gaussian_delays(len(grupo), wave_duration, seed=f"wave:{hora}:{depto}")

                for (tarjeta, actual, objetivo), delay in zip(grupo, delays):
                    destino_lobby = pos_random(tarjeta, "lobby")
                    vel_individual = velocidad_hormiga(f"{tarjeta}:{hora}")
                    run_time = (base_entrada / velocidad_entrada) * vel_individual
                    pausa = micro_pausa(f"{tarjeta}:{hora}:pausa")

                    anim = mover_lineal(dots[tarjeta], destino_lobby, run_time=run_time)
                    if anim:
                        if pausa > 0:
                            wave_in.append(Succession(Wait(delay), anim, Wait(pausa)))
                        else:
                            wave_in.append(Succession(Wait(delay), anim))

                if wave_in:
                    self.play(AnimationGroup(*wave_in, lag_ratio=0.0))
                    for tarjeta, _, _ in grupo:
                        zona_actual[tarjeta] = "lobby"

                # FASE 2: Subir a su piso (mismo grupo de color)
                wave_up = []
                up_delays = gaussian_delays(len(grupo), wave_duration * 0.6, seed=f"up:{hora}:{depto}")
                for (tarjeta, actual, objetivo), delay in zip(grupo, up_delays):
                    if objetivo == "lobby":
                        zona_actual[tarjeta] = objetivo
                        continue
                    destino = pos_random(tarjeta, objetivo)
                    vel_individual = velocidad_hormiga(f"{tarjeta}:{hora}:up")
                    run_time = (base_escalera / velocidad_escalera) * vel_individual
                    anim = mover_por_escalera(dots[tarjeta], destino, run_time=run_time)
                    if anim:
                        wave_up.append(Succession(Wait(delay), anim))
                    zona_actual[tarjeta] = objetivo

                if wave_up:
                    self.play(AnimationGroup(*wave_up, lag_ratio=0.0))

            # Actualizar hora en timeline
            hora_label = Text(f"{hora:02d}:00", font_size=16, color=WHITE)
            hora_label.move_to(hora_text.get_center())
            self.play(Transform(hora_text, hora_label), run_time=0.3)

            wave_out = []
            out_delays = gaussian_delays(len(saliendo), wave_duration * 0.7, seed=f"out:{hora}")
            for (tarjeta, actual, objetivo), delay in zip(saliendo, out_delays):
                destino = pos_random(tarjeta, objetivo)
                vel_individual = velocidad_hormiga(f"{tarjeta}:{hora}:out")
                run_time = (base_salida / velocidad_salida) * vel_individual
                pausa = micro_pausa(f"{tarjeta}:{hora}:out:pausa")
                anim = mover_por_escalera(dots[tarjeta], destino, run_time=run_time)
                if anim:
                    if pausa > 0:
                        wave_out.append(Succession(Wait(delay), anim, Wait(pausa)))
                    else:
                        wave_out.append(Succession(Wait(delay), anim))
                zona_actual[tarjeta] = objetivo

            if wave_out:
                self.play(
                    AnimationGroup(*wave_out, lag_ratio=0.0)
                )

            wave_internal = []
            int_delays = gaussian_delays(len(internos), wave_duration * 0.5, seed=f"int:{hora}")
            for (tarjeta, actual, objetivo), delay in zip(internos, int_delays):
                destino = pos_random(tarjeta, objetivo)
                vel_individual = velocidad_hormiga(f"{tarjeta}:{hora}:int")
                run_time = (base_interno / velocidad_interno) * vel_individual
                anim = mover_por_escalera(dots[tarjeta], destino, run_time=run_time)
                if anim:
                    wave_internal.append(Succession(Wait(delay), anim))
                zona_actual[tarjeta] = objetivo

            if wave_internal:
                self.play(
                    AnimationGroup(*wave_internal, lag_ratio=0.0)
                )

            marcador_destino = puntos[hora].get_center()
            if not np.allclose(prev_marker_pos, marcador_destino):
                tramo = Line(prev_marker_pos, marcador_destino)
                self.play(
                    MoveAlongPath(marcador, tramo, rate_func=linear),
                    run_time=timeline_slide_seconds
                )
                prev_marker_pos = marcador_destino

            nuevo_in = Text(f"Dentro: {ocupacion_dentro}", font_size=20, color="#50C878").move_to(contador_in.get_center())
            nuevo_out = Text(f"Fuera: {ocupacion_fuera}", font_size=20, color="#E74C3C").move_to(contador_out.get_center())
            self.play(Transform(contador_in, nuevo_in), Transform(contador_out, nuevo_out), run_time=0.2)

        self.wait(2)

        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )

    def mostrar_error(self, mensaje: str):
        error_text = Text(
            f"ERROR: {mensaje}",
            font_size=24,
            color=RED
        )
        self.play(Write(error_text))
        self.wait(3)
