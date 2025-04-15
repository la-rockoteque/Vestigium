import { compile } from '@mdx-js/mdx'
import { readFileSync, writeFileSync } from 'fs'
import React from 'react'
import ReactDOMServer from 'react-dom/server'
import { jsx as _jsx, jsxs as _jsxs } from 'react/jsx-runtime'
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import path from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Make React and the JSX helpers available globally
global.React = React
global._jsx = _jsx
global._jsxs = _jsxs

// Read the MDX source file.
const source_name = process.argv[2]
const filename = process.argv[3]

const source = readFileSync(path.resolve(__dirname, `../out/${source_name}/${filename}.mdx`), 'utf-8')
const base_css = readFileSync(path.resolve(__dirname, `../src/style/base.css`), 'utf-8')
const source_css = readFileSync(path.resolve(__dirname, `../src/style/${source_name}.css`), "utf8");
const section_css = readFileSync(path.resolve(__dirname, `../src/style/${filename}.css`), "utf8");
const outputFile = path.resolve(__dirname, `../out/${source_name}/${filename}.html`)
// Define a fallback Image component that renders a standard <img> element.
function ImageFallback(props) {
    return React.createElement('img', props)
}

// Define Layout using the inlined CSS.
function Layout({ children }) {
    return React.createElement(
        "html",
        null,
        React.createElement(
            "head",
            null,
            React.createElement("meta", {charSet: "utf-8"}),
            React.createElement("title", null, "Styled MDX Content"),
            // Inline the external CSS:
            React.createElement("link", { rel: "stylesheet", href: "https://fonts.googleapis.com" }),
            React.createElement("link", { rel: "stylesheet", href: "https://fonts.gstatic.com" }),
            React.createElement("link", { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Cedarville+Cursive&family=Oswald:wght@200..700&family=Permanent+Marker&display=swap" }),
    
            React.createElement("style", null, base_css),
            React.createElement("style", null, source_css),
            React.createElement("style", null, section_css)
),
    React.createElement("body", null,
        React.createElement("div", {className: "two-columns"}, children)
    )
)
    ;
}

// Compile the MDX source using default options.
compile(source, {outputFormat: 'function-body'})
    .then(compiled => {
        const code = compiled.value || compiled.code;
        const fn = new Function(code);
        const MDXExport = fn({
            Fragment: React.Fragment,
            jsx: _jsx,
            jsxs: _jsxs
        });
        const MDXContent = MDXExport.default || MDXExport;
        // Now pass the components prop when creating the element.
        const element = React.createElement(
            Layout,
            null,
            React.createElement(MDXContent, {components: {Image: ImageFallback}})
        );
        const html = ReactDOMServer.renderToStaticMarkup(element);
        writeFileSync(outputFile, html);
        console.log('Conversion successful!');
    })
    .catch(err => {
        console.error(err);
        process.exit(1);
    });