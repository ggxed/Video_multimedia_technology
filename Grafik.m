clear;
close all;

corr1 = csvread('correlation.txt');
y1 = 1:1:length(corr1);
x1 = 1:1:length(corr1);
surf(x1, y1, corr1);

comp = csvread('correlation.txt');
y = 1:1:length(comp);
x = 1:1:length(comp);
surf(x, y, comp);
hold on;


grid on;
xlabel('x');
ylabel('y');
zlabel('r(x,y)');
figure;

comp = csvread('correlation2.txt');
y = 1:1:length(comp);
x = 1:1:length(comp);
surf(x, y, comp);
hold on;


grid on;
xlabel('x');
ylabel('y');
zlabel('r(x,y)');
figure;
comp = csvread('correlation3.txt');
y = 1:1:length(comp);
x = 1:1:length(comp);
surf(x, y, comp);
hold on;


grid on;
xlabel('x');
ylabel('y');
zlabel('r(x,y)');
