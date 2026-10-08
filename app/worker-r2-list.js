const corsHeaders = {
	"Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "GET, OPTIONS",
	"Access-Control-Allow-Headers": "Content-Type",
	"Cache-Control": "no-store",
	"Content-Type": "application/json; charset=utf-8"
};

export default {
	async fetch(request, env) {
		const url = new URL(request.url);

		if (request.method === "OPTIONS") {
			return new Response(null, { headers: corsHeaders });
		}

		if (url.pathname !== "/api/nuvens") {
			return new Response("Not found", { status: 404 });
		}

		if (request.method !== "GET") {
			return new Response("Method not allowed", {
				status: 405,
				headers: corsHeaders
			});
		}

		if (!env.NUVENS_R2) {
			return Response.json({ error: "Configure o binding NUVENS_R2 para o bucket R2." }, {
				status: 500,
				headers: corsHeaders
			});
		}

		const options = { limit: 1000 };
		const prefix = env.R2_PREFIX || "";
		if (prefix) options.prefix = prefix;

		const cursor = url.searchParams.get("cursor");
		if (cursor) options.cursor = cursor;

		let resultado;
		try {
			resultado = await env.NUVENS_R2.list(options);
		} catch (error) {
			console.error("Falha ao listar objetos no bucket R2:", error);
			return Response.json({ error: "Falha ao consultar o bucket R2." }, {
				status: 502,
				headers: corsHeaders
			});
		}

		const objects = resultado.objects
			.filter(objeto => objeto.key.toLowerCase().endsWith(".copc.laz"))
			.map(objeto => ({ key: objeto.key, size: objeto.size }));

		return Response.json({
			objects,
			truncated: resultado.truncated,
			nextCursor: resultado.truncated ? resultado.cursor : null
		}, { headers: corsHeaders });
	}
};
