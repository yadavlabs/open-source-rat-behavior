%% Figure_6_plots.m
% script for plotting rat behavior data in Figure 6

%% load data
file_names = {dir().name};
file_names_ap = file_names(contains(file_names, 'Rat1')); %alternating ports (fig 6a,b)
file_names_scs = file_names(contains(file_names, 'Rat2')); % scs detection (fig 6c)

data_label = readcell(file_names_ap{1}, 'Sheet','Sheet1','Range','A1:L1');
data_ap = cellfun(@(fn) readmatrix(fn, 'Sheet','Sheet1','Range','A2'), file_names_ap, "UniformOutput", false);
data_scs_raw = cellfun(@(fn) readmatrix(fn, 'Sheet','Sheet1','Range','A2'), file_names_scs, "UniformOutput", false);

trial_col = find(ismember(data_label, 'Trial'));
type_col = find(ismember(data_label, 'Type'));
response_col = find(ismember(data_label, 'Response'));
forced_col = find(ismember(data_label, 'Forced'));
correct_col = find(ismember(data_label, 'Correct'));
randomized_col = find(ismember(data_label, 'Randomized'));
amplitude_col = find(ismember(data_label, 'Amplitude (uA)'));

%% alternating ports
no_response_fraction = cellfun(@(d) nnz(d(:,response_col) == 5)/d(end,trial_col), data_ap);
forced_fraction = cellfun(@(d) sum(d(:,forced_col))/d(end,trial_col), data_ap);
fraction_correct_ap = cellfun(@(d) nnz(d(:,correct_col) == 1) / (d(end,trial_col) - nnz(d(:,correct_col) == 5)), data_ap);

%% detection
data_scs = cell2mat(data_scs_raw');
data_scs(data_scs(:,type_col) == 2, :) = [];
data_scs(data_scs(:,randomized_col) == 0, :) = [];
data_scs(data_scs(:,response_col) == 5, :) = [];
amplitudes = unique(data_scs(:, amplitude_col));
[gc,grps] = groupcounts(data_scs(:,contains(data_label,"Amplitude") | contains(data_label,"Correct")),'IncludeEmptyGroups',1);
grps = cell2mat(grps);
grps_label = grps(grps(:,1) == 1);
correct = gc(grps(:,1) == 1);
incorrect = gc(grps(:,1) == 0);
total = correct + incorrect;
fraction_correct = correct./total;

xstep = amplitudes(2) - amplitudes(1);
X = (amplitudes-amplitudes(1))'/xstep;

%% plots
%% fig 6a
figure('Name', '6a');
bar([no_response_fraction' forced_fraction'])
xlabel('Days')
ylabel('Fraction of Trials')
yticks([0 0.4])
lgn_6a = legend('No-response Trials', 'Forced Trials');
lgn_6a.Box = "off";
box off

%% fig 6b
figure('Name', '6b');
plot(fraction_correct_ap, 'LineWidth', 2, 'LineStyle','-', 'Marker', 'o', 'MarkerFaceColor', [0.00,0.45,0.74])
xlabel('Days')
ylabel('Fraction Correct')
xticks(1:length(data_ap))
yticks([0.55 0.8])
box off

%% fig 6c
figure('Name', '6c');
[~,~,x_threshold_norm]=sigm_fit(X,fraction_correct,[0.52 1 NaN 1.61],[],1,[0.00,0.45,0.74],0.75,[]);
x_threshold = x_threshold_norm*xstep+amplitudes(1);
hold on
x_line = ones(1,length(X));
x_line2 = linspace(0,x_threshold_norm,5);
yp = linspace(0.3,0.75,10);
yth = ones(1,5)*0.75;
plot(x_line*x_threshold_norm,yp,'--','color','k')
plot(x_line2,yth,'--','color','k')
xticks([0 3 6 9])
xticklabels(split(num2str([25 100 175 250])))
yticks([0.3 0.75 1.0])
yticklabels({'0.30', '0.75', '1.00'})
text(3.55, 0.75, ['Threshold = ' num2str(x_threshold) ' uA'])
xlabel('Amplitude (uA)')
ylabel('Fraction Detected')
box off
