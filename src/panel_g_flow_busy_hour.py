from manim import *
import os
import sys
from pathlib import Path
from datetime import datetime
import random
import numpy as np
from collections import defaultdict
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
        # CONFIG PANEL
        # ========================================
        panel_cfg = {}
        cfg_path = Path(__file__).parent / "config" / "paneles.yaml"
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                panel_cfg = yaml.safe_load(f) or {}
        panel_cfg = panel_cfg.get("panel_g_flow_busy_hour", {})

        elevator_capacity = int(panel_cfg.get("elevator_capacity", 6))
        elevator_trip_limit = int(panel_cfg.get("elevator_trip_limit", 3))
        patience_trips = int(panel_cfg.get("patience_trips", elevator_trip_limit))
        timeline_slide_seconds = float(panel_cfg.get("timeline_slide_seconds", 0.4))
        people_move_seconds = float(panel_cfg.get("people_move_seconds", 0.6))

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
            "fuera": (-6.5, -3.5, -1.6, 1.6),
            "lobby": (building_center_x - 2.8, building_center_x + 2.8, floor_centers[0] - 0.35, floor_centers[0] + 0.35),
            "depto_a": (building_center_x - 2.8, building_center_x + 2.8, floor_centers[1] - 0.35, floor_centers[1] + 0.35),
            "depto_b": (building_center_x - 2.8, building_center_x - 0.2, floor_centers[2] - 0.35, floor_centers[2] + 0.35),
            "depto_c": (building_center_x + 0.2, building_center_x + 2.8, floor_centers[2] - 0.35, floor_centers[2] + 0.35),
            "casino": (building_center_x - 2.8, building_center_x + 2.8, floor_centers[3] - 0.35, floor_centers[3] + 0.35),
        }

        elevator_lobby = [elevator_x, floor_centers[0], 0]
        stairs_lobby = [stairs_x, floor_centers[0], 0]

        # Contadores IN/OUT
        total_in = 0
        total_out = 0
        contador_in = Text("IN eventos: 0", font_size=20, color="#50C878")
        contador_out = Text("OUT eventos: 0", font_size=20, color="#E74C3C")
        total_text = Text(f"Personas: {total_personas}", font_size=18, color=WHITE)
        asistencia_text = Text(f"Asistencia: {asistencia_pct:.1f}%", font_size=18, color=WHITE)
        contador_in.to_corner(UR, buff=0.6)
        contador_out.next_to(contador_in, DOWN, buff=0.2, aligned_edge=RIGHT)
        total_text.next_to(contador_out, DOWN, buff=0.2, aligned_edge=RIGHT)
        asistencia_text.next_to(total_text, DOWN, buff=0.2, aligned_edge=RIGHT)
        self.play(FadeIn(contador_in), FadeIn(contador_out), FadeIn(total_text), FadeIn(asistencia_text))

        def pos_random(tarjeta: str, zona: str) -> list:
            xmin, xmax, ymin, ymax = zonas[zona]
            seed = f"{tarjeta}:{zona}"
            rng = random.Random(seed)
            return [rng.uniform(xmin, xmax), rng.uniform(ymin, ymax), 0]

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

        zone_floor = {
            "fuera": -1,
            "lobby": 0,
            "depto_a": 1,
            "depto_b": 2,
            "depto_c": 2,
            "casino": 3,
        }

        elevator_floor = 0
        elevator_capacity = max(1, elevator_capacity)
        elevator_trip_limit = max(1, elevator_trip_limit)
        patience_trips = max(1, patience_trips)
        def animar_puertas(abre: bool):
            cab_center = elevator_cab.get_center()
            door_left_closed = cab_center + LEFT * (cab_width * 0.15)
            door_right_closed = cab_center + RIGHT * (cab_width * 0.15)
            door_left_open = cab_center + LEFT * (cab_width * 0.33)
            door_right_open = cab_center + RIGHT * (cab_width * 0.33)
            if abre:
                return AnimationGroup(
                    door_left.animate.move_to(door_left_open),
                    door_right.animate.move_to(door_right_open),
                    lag_ratio=0
                )
            return AnimationGroup(
                door_left.animate.move_to(door_left_closed),
                door_right.animate.move_to(door_right_closed),
                lag_ratio=0
            )

        def mover_elevador(hacia_floor: int):
            nonlocal elevator_floor
            destino_y = floor_centers[hacia_floor]
            anim = elevator.animate.move_to([elevator_x, destino_y, 0])
            elevator_floor = hacia_floor
            return anim

        def mover_por_escalera(dot, destino, run_time=0.3):
            start = dot.get_center()
            if np.allclose(start, destino):
                return None
            p1 = np.array([stairs_x, floor_centers[0], 0])
            p2 = np.array([stairs_x, destino[1], 0])
            path = VMobject()
            path.set_points_as_corners([start, p1, p2, destino])
            return MoveAlongPath(dot, path, rate_func=linear, run_time=run_time)

        def mover_por_elevador(dot, destino, run_time=0.3):
            start = dot.get_center()
            if np.allclose(start, destino):
                return None
            p1 = np.array([elevator_x, floor_centers[0], 0])
            p2 = np.array([elevator_x, destino[1], 0])
            path = VMobject()
            path.set_points_as_corners([start, p1, p2, destino])
            return MoveAlongPath(dot, path, rate_func=linear, run_time=run_time)

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
            total_in += sum(1 for _, e in eventos_hora if e.get("tipo") == "entrada")
            total_out += sum(1 for _, e in eventos_hora if e.get("tipo") == "salida")
            for _, evento in eventos_hora:
                aplicar_evento(evento)

            animaciones = []
            movimientos = []
            for tarjeta, dot in dots.items():
                actual = zona_actual[tarjeta]
                objetivo = estado[tarjeta]
                if actual != objetivo:
                    movimientos.append((tarjeta, actual, objetivo))

            # Seleccion para elevator vs escaleras
            elegibles = []
            for tarjeta, actual, objetivo in movimientos:
                if zone_floor.get(actual, -1) >= 0 or zone_floor.get(objetivo, -1) >= 0:
                    elegibles.append((tarjeta, actual, objetivo))

            elegibles.sort(key=lambda x: x[0])
            elevator_candidatos = elegibles[:elevator_capacity * patience_trips]
            elevator_set = {t[0] for t in elevator_candidatos}

            # Si hay mas pisos que viajes, el resto usa escaleras
            targets_by_floor = defaultdict(list)
            for tarjeta, actual, objetivo in elevator_candidatos:
                floor = max(zone_floor.get(objetivo, 0), 0)
                targets_by_floor[floor].append((tarjeta, actual, objetivo))

            if len(targets_by_floor.keys()) > elevator_trip_limit:
                floors_sorted = sorted(targets_by_floor.items(), key=lambda item: len(item[1]), reverse=True)
                allowed = {f for f, _ in floors_sorted[:elevator_trip_limit]}
                for floor, items in list(targets_by_floor.items()):
                    if floor not in allowed:
                        for tarjeta, actual, objetivo in items:
                            elevator_set.discard(tarjeta)
                        del targets_by_floor[floor]

            for tarjeta, actual, objetivo in movimientos:
                if tarjeta in elevator_set:
                    continue
                anim = mover_por_escalera(dots[tarjeta], stairs_lobby, run_time=0.2)
                if anim:
                    animaciones.append(anim)

            hora_label = Text(f"{hora:02d}:00", font_size=16, color=WHITE)
            hora_label.move_to(hora_text.get_center())

            if animaciones:
                self.play(
                    AnimationGroup(*animaciones, lag_ratio=0.01),
                    Transform(hora_text, hora_label),
                    run_time=people_move_seconds
                )
            else:
                self.play(
                    Transform(hora_text, hora_label),
                    run_time=0.3
                )

            # Elevador: max 3 viajes por hora
            viajes = 0
            # Elevador: mover a lobby primero
            for tarjeta, actual, objetivo in elevator_candidatos:
                if tarjeta in elevator_set:
                    anim = mover_por_elevador(dots[tarjeta], elevator_lobby, run_time=0.2)
                    if anim:
                        self.play(anim)

            for floor in sorted(targets_by_floor.keys()):
                if viajes >= elevator_trip_limit:
                    break
                grupo = targets_by_floor[floor][:elevator_capacity]
                overflow = targets_by_floor[floor][elevator_capacity:]
                for tarjeta, actual, objetivo in overflow:
                    anim = mover_por_escalera(dots[tarjeta], stairs_lobby, run_time=0.2)
                    if anim:
                        self.play(anim)
                    destino = pos_random(tarjeta, objetivo)
                    anim = mover_por_escalera(dots[tarjeta], destino, run_time=0.3)
                    if anim:
                        self.play(anim)
                    zona_actual[tarjeta] = objetivo
                if not grupo:
                    continue

                anims = []
                for tarjeta, actual, objetivo in grupo:
                    destino = pos_random(tarjeta, objetivo)
                    anim = mover_por_elevador(dots[tarjeta], destino, run_time=0.3)
                    if anim:
                        anims.append(anim)
                    zona_actual[tarjeta] = objetivo

                self.play(mover_elevador(floor), run_time=0.3)
                self.play(animar_puertas(True), run_time=0.15)
                if anims:
                    self.play(AnimationGroup(*anims, lag_ratio=0.02), run_time=0.4)
                self.play(animar_puertas(False), run_time=0.15)
                viajes += 1

            for tarjeta, actual, objetivo in movimientos:
                if tarjeta in elevator_set:
                    continue
                destino = pos_random(tarjeta, objetivo)
                anim = mover_por_escalera(dots[tarjeta], destino, run_time=0.3)
                if anim:
                    self.play(anim)
                zona_actual[tarjeta] = objetivo

            marcador_destino = puntos[hora].get_center()
            if not np.allclose(prev_marker_pos, marcador_destino):
                tramo = Line(prev_marker_pos, marcador_destino)
                self.play(
                    MoveAlongPath(marcador, tramo, rate_func=linear),
                    run_time=timeline_slide_seconds
                )
                prev_marker_pos = marcador_destino

            nuevo_in = Text(f"IN eventos: {total_in}", font_size=20, color="#50C878").move_to(contador_in.get_center())
            nuevo_out = Text(f"OUT eventos: {total_out}", font_size=20, color="#E74C3C").move_to(contador_out.get_center())
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
