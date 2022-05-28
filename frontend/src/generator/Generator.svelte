<script>
	import { onMount } from 'svelte';
	import conf from '../conf.js';

    const URL_PREFIX = conf.url_meet;

    let qrcodeElement;
    let qrcodeContent;
    let qrcodeGenerator;

	onMount(async () => {
		qrcodeGenerator =  new QRCode(qrcodeElement);
		displayNewCode();
	});

    function displayNewCode() {
        qrcodeGenerator.clear();
        qrcodeContent = generateNewUrl();
        qrcodeGenerator.makeCode(qrcodeContent);
    }

    function generateNewUrl() {
        return `${URL_PREFIX}/${base62(12)}`;
    }
</script>


<main>
	<h1>QR Meet Generator</h1>
	<div id="qrcode" bind:this={qrcodeElement}></div>
	<p>{qrcodeContent}</p>
	<button on:click={displayNewCode}>
	    Generate New QR Code
    </button>
</main>


<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

    #qrcode {
		display: flex;
		align-items: center;
		justify-content: center;
    }

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>