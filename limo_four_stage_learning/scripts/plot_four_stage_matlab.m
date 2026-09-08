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
        'axis background/.style={fill=white}', ...
        'axis line style={black}', ...
        'tick style={black}', ...
        'tick label style={font=\large,text=black}', ...
        'label style={font=\large,text=black}', ...
        'title style={font=\Large,text=black}', ...
        'legend style={font=\large,fill=white,draw=black,text=black}' ...
    } ...
};

%% 1. Ground-truth velocity
velocity_data = load("mat_data/ground_truth_velocity.mat");
figure('Name', 'Ground-truth velocity');
plot(velocity_data.time, velocity_data.velocity, ...
     'Color', [0 0.4470 0.7410], 'DisplayName', '$v(t)$');
hold on;
stairs(velocity_data.reference_time, velocity_data.reference, ...
       '--', 'Color', [0.8500 0.3250 0.0980], ...
       'DisplayName', '$v_{\mathrm{ref}}$');
hold off;
xlabel('Experiment time [s]', 'Interpreter', 'latex');
ylabel('Velocity [m/s]', 'Interpreter', 'latex');
% title('LIMO ground-truth velocity', 'Interpreter', 'latex');
velocity_legend = legend('Location', 'northeast', 'Interpreter', 'latex');
velocity_legend.Color = 'white';
velocity_legend.TextColor = 'black';
velocity_legend.EdgeColor = 'black';
grid on;
box on
set(gcf,'Color','w');
set(gca,'Color','w');
set(gca,'XColor','k');
set(gca,'YColor','k');
set(gca,'FontSize',32);

velocity_min = min([velocity_data.velocity(:); velocity_data.reference(:)]);
velocity_max = max([velocity_data.velocity(:); velocity_data.reference(:)]);
velocity_range = velocity_max - velocity_min;
velocity_margin = max(0.05, 0.08 * velocity_range);
ylim([velocity_min - velocity_margin, velocity_max + velocity_margin]);

matlab2tikz('tex/ground_truth_velocity.tex');

%% 2. Learned and model Hamiltonian gradients
gradient_data = load("mat_data/hamiltonian_gradients.mat");

% Limit the number of coordinates written by matlab2tikz. The source .mat
% file remains untouched; only this plotted/exported representation is
% downsampled. Include the last sample explicitly when it is off the stride.
gradient_max_points = 1000;
gradient_sample_count = min( ...
    numel(gradient_data.learned_time), ...
    numel(gradient_data.model_time));
gradient_stride = max(1, ceil(gradient_sample_count / gradient_max_points));
gradient_indices = 1:gradient_stride:gradient_sample_count;
if gradient_indices(end) ~= gradient_sample_count
    gradient_indices(end + 1) = gradient_sample_count;
end

learned_time_plot = gradient_data.learned_time(gradient_indices);
learned_gradient_plot = gradient_data.learned_gradient(gradient_indices);
model_time_plot = gradient_data.model_time(gradient_indices);
model_gradient_plot = gradient_data.model_gradient(gradient_indices);

fprintf('Hamiltonian-gradient export: %d of %d samples per curve.\n', ...
        numel(gradient_indices), gradient_sample_count);

gradient_figure = figure('Name', 'Hamiltonian gradients', 'Color', 'w');

plot(learned_time_plot, ...
     learned_gradient_plot, ...
     'Color', [0 0.4470 0.7410], ...
     'DisplayName', 'Learned');
hold on;

plot(model_time_plot, ...
     model_gradient_plot, ...
     'Color', [0.8500 0.3250 0.0980], ...
     'DisplayName', 'Model');
hold off;

xlabel('Experiment time [s]', 'Interpreter', 'latex');
ylabel('$\nabla_u H$', 'Interpreter', 'latex');

lgd = legend('Location', 'northeast', 'Interpreter', 'latex');
lgd.Color = 'white';
lgd.TextColor = 'black';
lgd.EdgeColor = 'black';
lgd.Box = 'on';

grid on;
box on;

ax = gca;
ax.Color = 'white';
ax.XColor = 'black';
ax.YColor = 'black';
ax.FontSize = 32;

% Inset: enlarge the first 40 seconds without changing the main axes.
inset_mask = learned_time_plot >= 0 & learned_time_plot <= 40;
inset_ax = axes( ...
    'Parent', gradient_figure, ...
    'Position', [0.32 0.58 0.36 0.34], ...
    'Color', 'white', ...
    'XColor', 'black', ...
    'YColor', 'black', ...
    'FontSize', 18, ...
    'Box', 'on');
plot(inset_ax, learned_time_plot(inset_mask), ...
     learned_gradient_plot(inset_mask), ...
     'Color', [0 0.4470 0.7410]);
hold(inset_ax, 'on');
plot(inset_ax, model_time_plot(inset_mask), ...
     model_gradient_plot(inset_mask), ...
     'Color', [0.8500 0.3250 0.0980]);
hold(inset_ax, 'off');
xlim(inset_ax, [0 40]);

inset_values = [learned_gradient_plot(inset_mask), ...
                model_gradient_plot(inset_mask)];
inset_min = min(inset_values);
inset_max = max(inset_values);
inset_range = inset_max - inset_min;
inset_margin = max(0.05, 0.08 * inset_range);
ylim(inset_ax, [inset_min - inset_margin, inset_max + inset_margin]);
title(inset_ax, '$0\leq t\leq40\,\mathrm{s}$', ...
      'Interpreter', 'latex', 'FontSize', 18, 'Color', 'black');
grid(inset_ax, 'on');

matlab2tikz( ...
    'tex/hamiltonian_gradients.tex', ...
    'width', '\figurewidth', ...
    'height', '\figureheight', ...
    'extraAxisOptions', { ...
        'axis background/.style={fill=white}', ...
        'axis line style={black}', ...
        'tick style={black}', ...
        'tick label style={text=black}', ...
        'label style={text=black}', ...
        'title style={text=black}', ...
        'legend style={fill=white,draw=black,text=black}' ...
    });

%% 3. Policy coefficients in one two-panel figure
slope_data = load('mat_data/policy_slope.mat');
intercept_data = load('mat_data/policy_intercept.mat');

policy_max_points = 1000;
policy_sample_count = min( ...
    numel(slope_data.time), numel(intercept_data.time));
policy_stride = max(1, ceil(policy_sample_count / policy_max_points));
policy_indices = 1:policy_stride:policy_sample_count;
if policy_indices(end) ~= policy_sample_count
    policy_indices(end + 1) = policy_sample_count;
end

policy_time_plot = slope_data.time(policy_indices);
policy_slope_plot = slope_data.policy_slope(policy_indices);
policy_intercept_plot = intercept_data.policy_intercept(policy_indices);

% The bag topics share the controller sample clock. Use the recorded
% reference schedule to select the correct optimal intercept by stage:
% k_0^*=0.29 for v_ref=0.6, and k_0^*=0 for v_ref=0.
if numel(velocity_data.reference) ~= policy_sample_count
    error('Reference and policy topics have different sample counts.');
end
optimal_intercept_plot = 0.29 * ...
    (velocity_data.reference(policy_indices) > 0.0);

fprintf('Policy export: %d of %d samples per subplot.\n', ...
        numel(policy_indices), policy_sample_count);

figure('Name', 'Policy coefficients', 'Color', 'w');

subplot(2, 1, 1);
plot(policy_time_plot, policy_slope_plot, ...
     'Color', [0 0.4470 0.7410], ...
     'DisplayName', '$k_1(t)$');
hold on;
plot([policy_time_plot(1), policy_time_plot(end)], [-1.30, -1.30], ...
     '--', 'Color', [0 0.4470 0.7410], ...
     'DisplayName', '$k_1^*$');
hold off;
ylabel('$k_1$', 'Interpreter', 'latex');
% slope_legend = legend('Location', 'northeast', 'Interpreter', 'latex');
% slope_legend.Color = 'white';
% slope_legend.TextColor = 'black';
% slope_legend.EdgeColor = 'black';
% slope_legend.Box = 'on';
grid on;
box on;
ax_slope = gca;
ax_slope.Color = 'white';
ax_slope.XColor = 'black';
ax_slope.YColor = 'black';
ax_slope.FontSize = 32;
ax_slope.XTickLabel = [];

subplot(2, 1, 2);
plot(policy_time_plot, policy_intercept_plot, ...
     'Color', [0.8500 0.3250 0.0980], ...
     'DisplayName', '$k_0(t)$');
hold on;
stairs(policy_time_plot, optimal_intercept_plot, ...
     '--', 'Color', [0.8500 0.3250 0.0980], ...
     'DisplayName', '$k_0^*$');
hold off;
xlabel('Experiment time [s]', 'Interpreter', 'latex');
ylabel('$k_0$', 'Interpreter', 'latex');
% intercept_legend = legend('Location', 'northeast', 'Interpreter', 'latex');
% intercept_legend.Color = 'white';
% intercept_legend.TextColor = 'black';
% intercept_legend.EdgeColor = 'black';
% intercept_legend.Box = 'on';
grid on;
box on;
ax_intercept = gca;
ax_intercept.Color = 'white';
ax_intercept.XColor = 'black';
ax_intercept.YColor = 'black';
ax_intercept.FontSize = 32;

% Pad the intercept limits so k_0(t) and k_0^* stay inside the axes box.
intercept_min = min([policy_intercept_plot(:); optimal_intercept_plot(:)]);
intercept_max = max([policy_intercept_plot(:); optimal_intercept_plot(:)]);
intercept_range = intercept_max - intercept_min;
intercept_margin = max(0.05, 0.08 * intercept_range);
ylim(ax_intercept, [intercept_min - intercept_margin, ...
                    intercept_max + intercept_margin]);

% Use identical horizontal limits and aligned plot boxes.
x_limits = [ ...
    min(policy_time_plot), ...
    max(policy_time_plot) ...
];
xlim(ax_slope, x_limits);
xlim(ax_intercept, x_limits);
linkaxes([ax_slope, ax_intercept], 'x');

matlab2tikz( ...
    fullfile(tex_dir, 'policy_coefficients.tex'), ...
    export_options{:});

fprintf('Saved matlab2tikz files to: %s\n', tex_dir);
