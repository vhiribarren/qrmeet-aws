<script>
import { v4 as uuidv4 } from 'uuid';
import { detectIncognito } from "detect-incognito";
import conf from "conf";


const KEYSTORE_LOCAL_ID = "qrmeet:localId";

const urlParams = new URLSearchParams(window.location.search);
const meetParam = urlParams.get('meet');


let fetchPromise;
let privateModePromise = detectIncognito();
let localId = localStorage.getItem(KEYSTORE_LOCAL_ID);


if (! localId) {
    localId = uuidv4();
    localStorage.setItem(KEYSTORE_LOCAL_ID, localId);
}


if (meetParam) {
    fetchPromise = fetch(`${conf.url_meet}?meet=${meetParam}&from=${localId}`);
}
</script>


<main>

    <h1>QR Meet</h1>

    {#await privateModePromise then result}
    <p>Private mode: {result.isPrivate}</p>
    {/await}

    <p>LocalId: {localId}</p>

    {#if meetParam}
    <p>MeetParam: {meetParam}</p>
    <p>Publish status:
    {#await fetchPromise}
        ...waiting
    {:then response}
        you successfully encountered {meetParam}
    {:catch error}
        <span style="color: red">Failed to submit {meetParam}</span>
    {/await}
    </p>
    {/if}

</main>


<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
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