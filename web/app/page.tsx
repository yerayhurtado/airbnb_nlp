"use client";

import { useState, useEffect } from "react";
import {
  valorarResena,
  fetchResenas,
  healthCheck,
  type ValorarResponse,
  type ResenaItem,
} from "@/lib/api";

function StarsDisplay({ estrellas }: { estrellas: number }) {
  const n = Math.max(0, Math.min(5, estrellas));
  return (
    <div className="flex text-[#222222] gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <iconify-icon
          key={i}
          icon="solar:star-bold"
          width="12"
          style={{ color: i <= n ? "#222222" : "#dddddd" }}
        />
      ))}
    </div>
  );
}

function StarsDisplayLarge({ estrellas }: { estrellas: number }) {
  const n = Math.max(0, Math.min(5, estrellas));
  return (
    <div className="flex gap-1 text-[#dddddd] transition-colors">
      {[1, 2, 3, 4, 5].map((i) => (
        <iconify-icon
          key={i}
          icon="solar:star-bold"
          width="28"
          style={{ color: i <= n ? "#222222" : "#dddddd" }}
        />
      ))}
    </div>
  );
}

function formatDate(dateStr: string) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  const months = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
  ];
  return `${months[d.getMonth()]} ${d.getFullYear()}`;
}

function AirbnbLogo({ className }: { className?: string }) {
  return (
    <svg
      role="img"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label="Airbnb"
    >
      <path
        fill="currentColor"
        d="M12.001 18.275c-1.353-1.697-2.148-3.184-2.413-4.457-.263-1.027-.16-1.848.291-2.465.477-.71 1.188-1.056 2.121-1.056s1.643.345 2.12 1.063c.446.61.558 1.432.286 2.465-.291 1.298-1.085 2.785-2.412 4.458zm9.601 1.14c-.185 1.246-1.034 2.28-2.2 2.783-2.253.98-4.483-.583-6.392-2.704 3.157-3.951 3.74-7.028 2.385-9.018-.795-1.14-1.933-1.695-3.394-1.695-2.944 0-4.563 2.49-3.927 5.382.37 1.565 1.352 3.343 2.917 5.332-.98 1.085-1.91 1.856-2.732 2.333-.636.344-1.245.558-1.828.609-2.679.399-4.778-2.2-3.825-4.88.132-.345.395-.98.845-1.961l.025-.053c1.464-3.178 3.242-6.79 5.285-10.795l.053-.132.58-1.116c.45-.822.635-1.19 1.351-1.643.346-.21.77-.315 1.246-.315.954 0 1.698.558 2.016 1.007.158.239.345.557.582.953l.558 1.089.08.159c2.041 4.004 3.821 7.608 5.279 10.794l.026.025.533 1.22.318.764c.243.613.294 1.222.213 1.858zm1.22-2.39c-.186-.583-.505-1.271-.9-2.094v-.03c-1.889-4.006-3.642-7.608-5.307-10.844l-.111-.163C15.317 1.461 14.468 0 12.001 0c-2.44 0-3.476 1.695-4.535 3.898l-.081.16c-1.669 3.236-3.421 6.843-5.303 10.847v.053l-.559 1.22c-.21.504-.317.768-.345.847C-.172 20.74 2.611 24 5.98 24c.027 0 .132 0 .265-.027h.372c1.75-.213 3.554-1.325 5.384-3.317 1.829 1.989 3.635 3.104 5.382 3.317h.372c.133.027.239.027.265.027 3.37.003 6.152-3.261 4.802-6.975z"
      />
    </svg>
  );
}

export default function Home() {
  const [resenas, setResenas] = useState<ResenaItem[]>([]);
  const [resenasLoading, setResenasLoading] = useState(false);
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [filtro, setFiltro] = useState("Todas");
  const [busqueda, setBusqueda] = useState("");
  const [orden, setOrden] = useState("recent");
  const [textoReview, setTextoReview] = useState("");
  const [resultado, setResultado] = useState<ValorarResponse | null>(null);
  const [valorando, setValorando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [certify, setCertify] = useState(false);
  const [pagina, setPagina] = useState(1);
  const porPagina = 12;

  const promedio =
    resenas.length > 0
      ? resenas.reduce((a, r) => a + r.puntuacion_media, 0) / resenas.length
      : 0;
  const promedioStr = promedio > 0 ? promedio.toFixed(2) : "—";

  useEffect(() => {
    healthCheck()
      .then((r) => setApiOk(r.ok && r.modelo_cargado))
      .catch(() => setApiOk(false));
  }, []);

  useEffect(() => {
    if (apiOk) {
      setResenasLoading(true);
      fetchResenas(1500)
        .then(setResenas)
        .catch(() => setError("Error al cargar reseñas"))
        .finally(() => setResenasLoading(false));
    }
  }, [apiOk]);

  let resenasFiltradas = filtro === "Todas" ? resenas : resenas.filter((r) => r.valoracion === filtro);
  if (busqueda.trim()) {
    const q = busqueda.toLowerCase();
    resenasFiltradas = resenasFiltradas.filter(
      (r) =>
        r.comments.toLowerCase().includes(q) ||
        (r.reviewer_name || "").toLowerCase().includes(q)
    );
  }
  if (orden === "highest") {
    resenasFiltradas = [...resenasFiltradas].sort((a, b) => b.puntuacion_media - a.puntuacion_media);
  } else if (orden === "lowest") {
    resenasFiltradas = [...resenasFiltradas].sort((a, b) => a.puntuacion_media - b.puntuacion_media);
  } else {
    resenasFiltradas = [...resenasFiltradas].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }

  const totalFiltradas = resenasFiltradas.length;
  const totalPaginas = Math.max(1, Math.ceil(totalFiltradas / porPagina));
  const paginaActual = Math.min(pagina, totalPaginas);
  const resenasPagina = resenasFiltradas.slice(
    (paginaActual - 1) * porPagina,
    paginaActual * porPagina
  );

  useEffect(() => {
    setPagina(1);
  }, [filtro, busqueda, orden]);

  async function handlePostReview() {
    if (!textoReview.trim() || !apiOk) return;
    setError(null);
    setResultado(null);
    setValorando(true);
    try {
      const r = await valorarResena(textoReview);
      setResultado(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al valorar");
    } finally {
      setValorando(false);
    }
  }

  const positivos = resenas.filter((r) => r.valoracion === "Positivo").length;
  const neutros = resenas.filter((r) => r.valoracion === "Neutro").length;
  const negativos = resenas.filter((r) => r.valoracion === "Negativo").length;
  const total = resenas.length;
  const pct = (v: number) => (total ? (v / total) * 100 : 0);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation con búsqueda de reseñas */}
      <nav className="sticky top-0 z-50 bg-white border-b border-[#ebebeb]">
        <div className="max-w-7xl mx-auto px-6 md:px-10 h-20 flex items-center relative">
          {/* Logo izquierda */}
          <div className="flex-1 flex justify-start min-w-0">
            <a href="#" className="hidden md:flex items-center gap-1.5 text-[#FF385C] shrink-0" aria-label="Airbnb">
              <AirbnbLogo className="w-8 h-8 flex-shrink-0" />
              <span className="text-xl font-bold tracking-tighter text-[#FF385C] hidden lg:block">airbnb</span>
            </a>
            <a href="#" className="md:hidden flex text-[#FF385C] shrink-0" aria-label="Airbnb">
              <AirbnbLogo className="w-8 h-8" />
            </a>
          </div>

          {/* Barra de búsqueda centrada */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-2 w-full max-w-xl px-2 pointer-events-none">
            <div className="flex-1 flex items-center min-h-[40px] pointer-events-auto">
              <div className="relative w-full">
                <span className="absolute left-0 top-0 bottom-0 flex items-center pl-3 pointer-events-none">
                  <iconify-icon icon="solar:magnifer-linear" className="text-[#717171]" width="18" />
                </span>
                <input
                  type="text"
                  placeholder="Buscar en reseñas..."
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  className="w-full bg-white border border-[#dddddd] rounded-full pl-10 pr-4 py-2.5 text-sm outline-none focus:ring-1 focus:ring-[#222222] focus:border-[#222222] transition-all placeholder:text-[#717171]"
                />
              </div>
            </div>
            <select
              value={filtro}
              onChange={(e) => setFiltro(e.target.value)}
              className="shrink-0 appearance-none bg-white border border-[#dddddd] text-[#222222] py-2.5 pl-3 pr-8 rounded-full text-sm font-medium focus:outline-none focus:border-[#222222] cursor-pointer pointer-events-auto"
            >
              <option value="Todas">Todas</option>
              <option value="Positivo">Positivas</option>
              <option value="Neutro">Neutras</option>
              <option value="Negativo">Negativas</option>
            </select>
            <select
              value={orden}
              onChange={(e) => setOrden(e.target.value)}
              className="shrink-0 appearance-none bg-white border border-[#dddddd] text-[#222222] py-2.5 pl-3 pr-8 rounded-full text-sm font-medium focus:outline-none focus:border-[#222222] cursor-pointer pointer-events-auto"
            >
              <option value="recent">Recientes</option>
              <option value="highest">Mejor</option>
              <option value="lowest">Peor</option>
            </select>
          </div>

          {/* Usuario derecha */}
          <div className="flex-1 flex justify-end items-center gap-2 min-w-0">  
            <button className="hover:bg-[#f7f7f7] p-3 rounded-full transition-colors hidden md:block">
              <iconify-icon icon="solar:globe-linear" className="text-[#222222] text-lg" />
            </button>
            <div className="flex items-center gap-3 pl-3 pr-1 py-1 border border-[#dddddd] rounded-full hover:shadow-md transition-shadow cursor-pointer ml-1">
              <iconify-icon icon="solar:hamburger-menu-linear" className="text-[#222222] text-lg" />
              <div className="bg-[#717171] text-white rounded-full w-8 h-8 flex items-center justify-center overflow-hidden">
                <iconify-icon icon="solar:user-bold" className="text-white text-lg mt-1" />
            </div>
          </div>
          </div>
        </div>
      </nav>

      <main className="flex-grow max-w-7xl mx-auto px-6 md:px-10 pt-10 w-full">        
        {!apiOk && (
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-sm">
            La API del modelo no está corriendo. Ejecuta: <code className="bg-amber-100 px-1 rounded">cd backend &amp;&amp; uvicorn main:app --reload --port 8000</code>
          </div>
        )}

        {/* Header Section */}
        <div className="border-b border-[#dddddd] pb-10 mb-10">
          <div className="flex flex-col items-center text-center gap-6">
            <div className="relative w-full max-w-sm">
              <div className="flex items-end justify-center gap-1 relative z-10">
                <iconify-icon icon="solar:leaf-bold" className="text-6xl text-[#E31C5F] -rotate-45 mb-4" />
                <span className="text-8xl font-extrabold tracking-tighter text-[#222222] leading-none">
                  {resenasLoading ? "—" : promedioStr}
                </span>
                <iconify-icon icon="solar:leaf-bold" className="text-6xl text-[#E31C5F] rotate-45 mb-4 flip-horizontal" />
              </div>
              <div className="mt-4 flex flex-col items-center">
                <div className="text-lg font-bold text-[#222222]">Valoración media de las reseñas</div>
                <div className="text-[#717171] text-base font-normal max-w-xs leading-snug">
                  Reseñas de Airbnb Barcelona valoradas con análisis de sentimiento (NLP)
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-lg font-semibold text-[#222222]">
                {resenasLoading ? "Cargando…" : `${resenas.length} reseñas`}
              </span>
            </div>
          </div>
        </div>

        {/* Rating breakdown - basado en nuestros datos (sentimiento) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-12 gap-y-4 mb-12">
          <div className="flex lg:flex-col lg:border-r border-[#dddddd] lg:pr-6 items-center lg:items-start justify-between gap-3">
            <div className="text-sm font-medium text-[#222222]">Positivas</div>
            <div className="flex-1 lg:w-full flex items-center gap-3">
              <span className="text-xs font-semibold text-[#222222] order-last lg:order-first">{pct(positivos).toFixed(0)}%</span>
              <div className="h-1 w-full bg-[#dddddd] rounded-full overflow-hidden">
                <div className="h-full bg-[#222222] rounded-full" style={{ width: `${pct(positivos)}%` }} />
              </div>
            </div>
          </div>
          <div className="flex lg:flex-col lg:border-r border-[#dddddd] lg:pr-6 items-center lg:items-start justify-between gap-3">
            <div className="text-sm font-medium text-[#222222]">Neutras</div>
            <div className="flex-1 lg:w-full flex items-center gap-3">
              <span className="text-xs font-semibold text-[#222222] order-last lg:order-first">{pct(neutros).toFixed(0)}%</span>
              <div className="h-1 w-full bg-[#dddddd] rounded-full overflow-hidden">
                <div className="h-full bg-[#222222] rounded-full" style={{ width: `${pct(neutros)}%` }} />
              </div>
            </div>
          </div>
          <div className="flex lg:flex-col lg:border-r border-[#dddddd] lg:pr-6 items-center lg:items-start justify-between gap-3">
            <div className="text-sm font-medium text-[#222222]">Negativas</div>
            <div className="flex-1 lg:w-full flex items-center gap-3">
              <span className="text-xs font-semibold text-[#222222] order-last lg:order-first">{pct(negativos).toFixed(0)}%</span>
              <div className="h-1 w-full bg-[#dddddd] rounded-full overflow-hidden">
                <div className="h-full bg-[#222222] rounded-full" style={{ width: `${pct(negativos)}%` }} />
              </div>
            </div>
          </div>
          <div className="flex lg:flex-col items-center lg:items-start justify-between gap-3">
            <div className="text-sm font-medium text-[#222222]">Puntuación media</div>
            <div className="flex-1 lg:w-full flex items-center gap-3">
              <span className="text-xs font-semibold text-[#222222] order-last lg:order-first">{promedioStr}/5</span>
              <div className="h-1 w-full bg-[#dddddd] rounded-full overflow-hidden">
                <div className="h-full bg-[#222222] rounded-full" style={{ width: `${total ? (promedio / 5) * 100 : 0}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* Valora tu reseña - sección destacada */}
        <div id="valorar-mi-resena" className="mb-12 p-6 md:p-8 bg-[#f7f7f7] border border-[#dddddd] rounded-2xl">
          <h3 className="text-xl font-semibold text-[#222222] mb-2">Escribe tu propia reseña y el modelo la valorará</h3>
          <p className="text-sm text-[#717171] mb-4">
            Escribe o pega aquí cualquier texto (por ejemplo una opinión de un alojamiento). El modelo NLP asignará estrellas (0-5) y una valoración (Positivo / Neutro / Negativo).
          </p>
          <div className="flex flex-col md:flex-row gap-4">
            <textarea
              value={textoReview}
              onChange={(e) => setTextoReview(e.target.value)}
              placeholder="Ej: El apartamento estaba impecable, muy buena ubicación. Repetiría sin dudar."
              className="flex-1 w-full bg-white border border-[#dddddd] rounded-xl p-4 text-base focus:ring-1 focus:ring-black focus:border-black outline-none transition-all placeholder:text-[#717171] min-h-[100px] resize-none"
            />
            <div className="flex flex-col gap-2 md:justify-center">
              <button
                onClick={handlePostReview}
                disabled={valorando || !textoReview.trim() || !apiOk}
                className="px-6 py-3 bg-[#E31C5F] text-white text-base font-semibold rounded-lg hover:bg-[#d90b4d] transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                {valorando ? "Valorando…" : "Valorar mi reseña"}
              </button>
              {resultado && (
                <div className="flex items-center gap-2 flex-wrap">
                  <StarsDisplayLarge estrellas={resultado.estrellas} />
                  <span className="text-sm font-semibold text-[#222222]">
                    {resultado.puntuacion_media}/5 — {resultado.valoracion}
                  </span>
                </div>
              )}
            </div>
          </div>
          {error && (
            <p className="mt-3 text-sm text-red-600">{error}</p>
          )}
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Reviews grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-20 gap-y-10">
          {resenasLoading ? (
            <p className="text-[#717171] col-span-2 py-8">Cargando reseñas…</p>
          ) : (
            resenasPagina.map((r) => (
              <div key={r.id} className="flex flex-col gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full overflow-hidden bg-[#dddddd]">
                    <img
                      src={`https://i.pravatar.cc/150?u=${encodeURIComponent(r.id)}`}
                      alt={r.reviewer_name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-[#222222]">{r.reviewer_name || "Anónimo"}</h3>
                    <p className="text-sm text-[#717171]">{formatDate(r.date)}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs text-[#222222] font-medium">
                    <StarsDisplay estrellas={r.estrellas} />
                    <span className="text-[#222222] text-xs">·</span>
                    <span className="text-[#717171] text-xs">{formatDate(r.date)}</span>
                    <span className="text-[#222222] text-xs">·</span>
                    <span className="text-[#717171] text-xs">{r.puntuacion_media}/5 · {r.valoracion}</span>
                  </div>
                  <p className="text-base leading-relaxed text-[#222222] font-normal">{r.comments}</p>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Paginación */}
        <div className="mt-12 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="text-[#717171] text-sm">
            {totalFiltradas === 0
              ? "No hay reseñas con este filtro"
              : `Mostrando ${(paginaActual - 1) * porPagina + 1}-${Math.min(paginaActual * porPagina, totalFiltradas)} de ${totalFiltradas} reseñas${totalFiltradas !== resenas.length ? ` (filtro de ${resenas.length})` : ""}`}
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPagina((p) => Math.max(1, p - 1))}
              disabled={paginaActual <= 1}
              className="px-4 py-2 border border-[#dddddd] rounded-lg text-sm font-medium text-[#222222] hover:bg-[#f7f7f7] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Anterior
            </button>
            <span className="text-sm text-[#717171] px-2">
              Página {paginaActual} de {totalPaginas}
            </span>
            <button
              type="button"
              onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
              disabled={paginaActual >= totalPaginas}
              className="px-4 py-2 border border-[#dddddd] rounded-lg text-sm font-medium text-[#222222] hover:bg-[#f7f7f7] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Siguiente
            </button>
          </div>
        </div>
      </main>

      <footer className="flex-none bottom-0 mt-8 border-t border-[#dddddd] bg-[#f7f7f7]">
        <div className="max-w-7xl mx-auto px-10 py-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-[#222222]">
          <div className="flex items-center gap-2">
            <span>© {new Date().getFullYear()} Airbnb Style — NLP Barcelona</span>
            <span>·</span>
            <a href="#" className="hover:underline">Privacidad</a>
            <span>·</span>
            <a href="#" className="hover:underline">Términos</a>
          </div>
          <div className="flex gap-4 font-semibold">
            <div className="flex items-center gap-1 cursor-pointer hover:underline">
              <iconify-icon icon="solar:globe-linear" />
              Español
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
