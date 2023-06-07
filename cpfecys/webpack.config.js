'use strict';

const path = require('path');
const webpack = require('webpack');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin')

module.exports = {
    entry: {
        home: './src/js/home.js',
        admin: './src/js/admin.js'
    },
    devtool: 'source-map',
    output: {
        path: path.resolve(__dirname, 'static/build/js'),
        filename: '[name].min.js'
    },
    module: {
        loaders: [
            {
                test: /\.js$/,
                loader: 'babel-loader',
                query: {
                    presets: ['es2015'],
                    plugins: [["transform-object-assign"], ["transform-es2015-for-of", {
                        "loose": true
                    }]]
                }
            }
        ]
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            "window.jQuery": "jquery",
            tether: 'tether',
            Tether: 'tether',
            'window.Tether': 'tether',
            Popper: ['popper.js', 'default'],
            'window.Tether': 'tether',
            Alert: 'exports-loader?Alert!bootstrap/js/dist/alert',
            Button: 'exports-loader?Button!bootstrap/js/dist/button',
            Carousel: 'exports-loader?Carousel!bootstrap/js/dist/carousel',
            Collapse: 'exports-loader?Collapse!bootstrap/js/dist/collapse',
            Dropdown: 'exports-loader?Dropdown!bootstrap/js/dist/dropdown',
            Modal: 'exports-loader?Modal!bootstrap/js/dist/modal',
            Popover: 'exports-loader?Popover!bootstrap/js/dist/popover',
            Scrollspy: 'exports-loader?Scrollspy!bootstrap/js/dist/scrollspy',
            Tab: 'exports-loader?Tab!bootstrap/js/dist/tab',
            Tooltip: "exports-loader?Tooltip!bootstrap/js/dist/tooltip",
            Util: 'exports-loader?Util!bootstrap/js/dist/util',
            Turbolinks: 'exports-loader?Util!turbolinks/dist/turbolinks'
        }),
        new UglifyJsPlugin({
            sourceMap: false,
            uglifyOptions: {
                ecma:8,  
                compress: {
                  warnings: false
                }
              }
        }),
    ],
    resolve: {
        extensions: ['.js', '.json']
    }
};
