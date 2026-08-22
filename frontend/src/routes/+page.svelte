<script lang="ts">
</script>

<main>
	<div class="splash">
		<h1>Alquiler</h1>
		<p>Sistema de Gestión de Alquileres</p>
		<div class="loading">
			<div class="spinner"></div>
			<span>Cargando...</span>
		</div>
	</div>
</main>

<style>
	:global(*) {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}

	:global(body) {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	main {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		width: 100%;
	}

	.splash {
		text-align: center;
		color: white;
		padding: 3rem;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 20px;
		backdrop-filter: blur(10px);
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
	}

	h1 {
		font-size: 3rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
	}

	p {
		font-size: 1.2rem;
		opacity: 0.9;
		margin-bottom: 2rem;
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
	}

	.spinner {
		width: 24px;
		height: 24px;
		border: 3px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	span {
		font-size: 1rem;
		opacity: 0.8;
	}
</style>
