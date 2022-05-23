<script>
import { v4 as uuidv4 } from 'uuid';
import conf from '../conf.json';

const KEYSTORE_LOCAL_ID = "qrmeet:localId";
const urlParams = new URLSearchParams(window.location.search);
const meetParam = urlParams.get('meet');

let fetchPromise;
let localId = localStorage.getItem(KEYSTORE_LOCAL_ID);


if (! localId) {
    localId = uuidv4();
    localStorage.setItem(KEYSTORE_LOCAL_ID, localId);
}


if (meetParam) {
    fetchPromise = fetch(`${conf.urlPrefixWithStorage}?meet=${meetParam}&from=${localId}`);
    }
</script>


<p>LocalId: {localId}</p>
<p>MeetParam: {meetParam}</p>

<p>Publish status: 

{#await fetchPromise}
	<p>...waiting</p>
{:then response}
	<p>The number is {response.ok}</p>
{:catch error}
	<p style="color: red">{error.message}</p>
{/await}

</p>