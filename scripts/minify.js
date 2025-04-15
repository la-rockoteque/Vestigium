import { readFileSync, writeFileSync } from 'fs'
import { jsonminify } from 'jsonminify'
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import path from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

const minified = jsonminify(readFileSync(path.join(__dirname, '../out/Velum_Cineris;everyday guide to concord city.json.json'), 'utf8'))
writeFileSync(path.join(__dirname, '../_generated/index-sources.json'), minified, 'utf8'))