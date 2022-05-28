import svelte from 'rollup-plugin-svelte';
import commonjs from '@rollup/plugin-commonjs';
import resolve from '@rollup/plugin-node-resolve';
import livereload from 'rollup-plugin-livereload';
import yaml from '@rollup/plugin-yaml';
import alias from '@rollup/plugin-alias';
import { terser } from 'rollup-plugin-terser';
import css from 'rollup-plugin-css-only';

const production = !process.env.ROLLUP_WATCH;
const qrmeetConfigName = process.env.QRMEET_CONFIG || "default";
const qrmeetConfigFile = `../config/${qrmeetConfigName}.yaml`;
const svelteFolders = [".", "ranking", "generator"]


function serve() {
	let server;

	function toExit() {
		if (server) server.kill(0);
	}

	return {
		writeBundle() {
			if (server) return;
			server = require('child_process').spawn('npm', ['run', 'start', '--', '--dev'], {
				stdio: ['ignore', 'inherit', 'inherit'],
				shell: true
			});

			process.on('SIGTERM', toExit);
			process.on('exit', toExit);
		}
	};
}

function svelteBuild(dir) {
	return {
		input: `src/${dir}/main.js`,
		output: {
			sourcemap: true,
			format: 'iife',
			name: 'app',
			file: `public/${dir}/build/bundle.js`
		},
		plugins: [
			svelte({
				compilerOptions: {
					// enable run-time checks when not in production
					dev: !production
				}
			}),
			// we'll extract any component CSS out into
			// a separate file - better for performance
			css({ output: 'bundle.css' }),
	
			// If you have external dependencies installed from
			// npm, you'll most likely need these plugins. In
			// some cases you'll need additional configuration -
			// consult the documentation for details:
			// https://github.com/rollup/plugins/tree/master/packages/commonjs
			resolve({
				browser: true,
				dedupe: ['svelte']
			}),
			commonjs(),

            alias({
				entries: [
					{ find: 'conf', replacement: qrmeetConfigFile}
				]
			}),

			// In dev mode, call `npm run start` once
			// the bundle has been generated
			!production && serve(),
	
			// Watch the `public` directory and refresh the
			// browser on changes when not in production
			!production && livereload('public'),
	
			// If we're building for production (npm run build
			// instead of npm run dev), minify
			production && terser(),
	
			yaml()
		],
		watch: {
			clearScreen: false
		}
	};
}


export default (function () {
	var ret = [];
	svelteFolders.forEach((folder) => ret.push(svelteBuild(folder)));
	return ret;
  })();