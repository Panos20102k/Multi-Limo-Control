%% Four-stage LIMO paper plots
% Load the .mat exports produced by plot_four_stage_bag.ipynb, recreate the
% four figures in MATLAB, and export PGFPlots/TikZ code with matlab2tikz.

clear;
close all;
clc;

script_dir = fileparts(mfilename('fullpath'));
data_dir = fullfile(script_dir, 'mat_data');
tex_dir = fullfile(script_dir, 'tex');
addpath('~/matlab2tikz/src/')

if ~isfolder(tex_dir)
    mkdir(tex_dir);
end

if exist('matlab2tikz', 'file') ~= 2
    error(['matlab2tikz is not on the MATLAB path. Install it and call ', ...
           'addpath(''/path/to/matlab2tikz/src'') before running this script.']);
end

set(groot, 'defaultAxesFontName', 'Times New Roman');
set(groot, 'defaultAxesFontSize', 10);
set(groot, 'defaultLineLineWidth', 1.2);
set(groot, 'defaultFigureColor', 'w');

export_options = { ...
    'width', '\figurewidth', ...
    'height', '\figureheight', ...
    'showInfo', false, ...
    'standalone', false, ...
    'parseStrings', false, ...
    'extraAxisOptions', { ...
        'tick label style={font=\large}', ...
        'label style={font=\large}', ...
        'title style={font=\Large}', ...
        'legend style={font=\large}' ...
    } ...
};

%% 1. Ground-truth velocity
velocity_data = load("mat_data/ground_truth_velocity.mat");
figure('Name', 'Ground-truth velocity');
plot(velocity_data.time, velocity_data.velocity, 'Color', [0 0.4470 0.7410]);
xlabel('Experiment time [s]', 'Interpreter', 'latex');
ylabel('Velocity [m/s]', 'Interpreter', 'latex');
% title('LIMO ground-truth velocity', 'Interpreter', 'latex');
grid on;
box on
set(gcf,'Color','w');
set(gca,'Color','w');
set(gca,'XColor','k');
set(gca,'YColor','k');
set(gca,'FontSize',32);
matlab2tikz('tex/ground_truth_velocity.tex');

%% 2. Learned and model Hamiltonian gradients
gradient_data = load(fullfile(data_dir, 'hamiltonian_gradients.mat'));
figure('Name', 'Hamiltonian gradients');
plot(gradient_data.learned_time, gradient_data.learned_gradient, ...
     'DisplayName', 'Learned gradient');
hold on;
plot(gradient_data.model_time, gradient_data.model_gradient, ...
     'DisplayName', 'Model gradient');
hold off;
xlabel('Experiment time [s]', 'Interpreter', 'latex');
ylabel('$\nabla_u H$', 'Interpreter', 'latex');
title('Hamiltonian gradients', 'Interpreter', 'latex');
legend('Location', 'best', 'Interpreter', 'latex');
grid on;
box on;
matlab2tikz(fullfile(tex_dir, 'hamiltonian_gradients.tex'), export_options{:});

%% 3. Policy slope
slope_data = load(fullfile(data_dir, 'policy_slope.mat'));
figure('Name', 'Policy slope');
plot(slope_data.time, slope_data.policy_slope, 'Color', [0.4660 0.6740 0.1880]);
xlabel('Experiment time [s]', 'Interpreter', 'latex');
ylabel('$k_e$', 'Interpreter', 'latex');
title('Policy slope', 'Interpreter', 'latex');
grid on;
box on;
matlab2tikz(fullfile(tex_dir, 'policy_slope.tex'), export_options{:});

%% 4. Policy intercept
intercept_data = load(fullfile(data_dir, 'policy_intercept.mat'));
figure('Name', 'Policy intercept');
plot(intercept_data.time, intercept_data.policy_intercept, ...
     'Color', [0.8500 0.3250 0.0980]);
xlabel('Experiment time [s]', 'Interpreter', 'latex');
ylabel('$k_0$', 'Interpreter', 'latex');
title('Policy intercept', 'Interpreter', 'latex');
grid on;
box on;
matlab2tikz(fullfile(tex_dir, 'policy_intercept.tex'), export_options{:});

fprintf('Saved matlab2tikz files to: %s\n', tex_dir);
