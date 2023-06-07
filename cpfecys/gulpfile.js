"use strict";

const gulp = require("gulp");
const cache = require("gulp-cache");
const fs = require("fs");
const less = require("gulp-less");
const sass = require("gulp-sass");
const webpack = require("webpack");
const webpackConfigDev = require("./webpack-dev.config");
const webpackConfig = require("./webpack.config");
const webpackstream = require("webpack-stream");
const gulpLoadPlugins = require('gulp-load-plugins');
const cleanCSS = require('gulp-clean-css');
const runSequence = require('run-sequence');
const imagemin = require("gulp-imagemin");
const imageminJpegRecompress = require('imagemin-jpeg-recompress');
const size = require("gulp-size");
const minifyCSS = require('gulp-minify-css');
const critical = require('critical');
const del = require('del');
const minify = require("gulp-minify");

var browserSync = require('browser-sync');
var nodemon = require('gulp-nodemon');

const $ = gulpLoadPlugins();
const config = {
  publicDir: './build',
};

gulp.task("styles", () => {
  return gulp.src('src/styles/*.scss')
    .pipe(sass().on('error', function (err) {
      console.log(err.toString());
      this.emit('end');
    }))
    .pipe(gulp.dest('static/build/css'))
    .pipe(browserSync.stream())
});

gulp.task('webpack-dev', () => {
  return gulp.src('src/js/**/*')
    .pipe(webpackstream(webpackConfigDev, webpack))
    .pipe(gulp.dest('static/build/js'))
});

gulp.task('webpack', () => {
  return gulp.src('src/js/**/*')
    .pipe(webpackstream(webpackConfig, webpack))
    .pipe(gulp.dest('static/build/js'))
});

gulp.task('minify-images', () => {
  return gulp.src(`src/images/**/*.*`)
    .pipe(
      cache(
        imagemin([
          imagemin.gifsicle({ interlaced: true }),
          imageminJpegRecompress({
            loops: 1,
            min: 88,
            max: 90
          }),
          imagemin.optipng({ optimizationLevel: 5 }),
          imagemin.svgo({ plugins: [{ removeViewBox: true }] })
        ])
      )
    )
    .pipe(gulp.dest('static/build/images'))
    .pipe(size({ title: 'images' }))
});

gulp.task('minify-css', gulp.series('styles', () => {
  return gulp.src('static/build/css/*.css')
    .pipe(minifyCSS())
    .pipe(gulp.dest('static/build/css'));
}));

gulp.task('clean', () => {
  return del(['build']);
});



gulp.task('critical', () => {
  critical.generate({
    base: './',
    inline: true,
    src: 'index.html',
    css: ['/static/build/css/styles.css'],
    dimensions: [{
      width: 320,
      height: 480
    }, {
      width: 768,
      height: 1024
    }, {
      width: 1280,
      height: 960
    }, {
      width: 1920,
      height: 1080
    }],
    dest: 'tmp/build/index.html',
    minify: true,
    extract: false,
    ignore: ['font-face']
  });
});

gulp.task('minify-js', () => {
  return gulp.src('src/js/*.js', { allowEmpty: true }) 
    .pipe(minify({noSource: true}))
    .pipe(gulp.dest('static/build/js'))
});

gulp.task('watch', gulp.series('clean', 'styles', 'minify-images', 'minify-js', () => {
  gulp.watch('src/styles/**/*.{scss,css}', gulp.series('styles'));
  gulp.watch('src/js/**/*', gulp.series('minify-js'));
}));

gulp.task('build', gulp.series('clean', 'minify-css', 'minify-images', 'minify-js'));
gulp.task('default', gulp.series('clean', 'styles', 'minify-images', 'webpack-dev'));