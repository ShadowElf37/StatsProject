class Participant:
    K = 32

    def __init__(self, name):
        self.name = name
        self.answers = []
        self.score = 0
        self.elo = [1000]
        self.expected_scores = []

    def calc_elo(self, participants, win: int):
        my_elo = self.elo[-1]
        other_elo = 0
        for p in participants:
            if p == self: continue
            other_elo += p.elo[-1]
        other_elo /= len(participants) - 1

        self.elo.append(my_elo + self.K * (win-self.expected_score(other_elo)))

    def expected_score(self, other_elo):
        s = 1 / (1 + 10**((other_elo-self.elo[-1])/400))
        self.expected_scores.append(s)
        return s


data = open('data.txt').read().split('\n')
names = data[0].split('\t')

ps = [Participant(name) for name in names]

for q, line in enumerate(data[1:]):
    for i, answer in enumerate(line.split('\t')):
        ps[i].answers.append(int(answer))
        ps[i].calc_elo(ps, int(answer))

print('Raw scores:')
for p in ps:
    p.score = sum(p.answers)
    print(p.name, p.score)


total_q = 40
q_control = 30

print(f'\nFirst {q_control} questions accuracy:')
for p in ps:
    print(p.name, round(sum(p.answers[:q_control])/q_control, 2))

print(f'\nLast {total_q-q_control} questions accuracy (i.e. predicted by score on first {q_control} questions):')
for p in ps:
    print(p.name, round(sum(p.answers[q_control:])/(total_q-q_control), 2))

print(f'\n{q_control}th question elo:')
for p in ps:
    print(p.name, round(p.elo[q_control+1]))

print(f'\nFinal elo:')
for p in ps:
    print(p.name, round(p.elo[-1]))

print(f'\nLast {total_q-q_control} questions Expected/Actual performance (from elo, constantly updated):')
for p in ps:
    print(p.name, round(sum(p.expected_scores[q_control:]), 2), '/', sum(p.answers[q_control:]))

print(f'\nLast {total_q-q_control} questions Expected/Actual performance (from elo, at question 30):')
for p in ps:
    print(p.name, round(p.expected_scores[q_control]*10, 2), '/', sum(p.answers[q_control:]))


import scipy.stats as stats

df = len(ps) - 1

chi2 = 0
for p in ps:
    expected = sum(p.answers[:q_control])
    observed = sum(p.answers[q_control:])
    chi2 += (observed - expected) ** 2 / expected

print('\nRAW GRADE χ^2 STATISTICS')
print('χ^2 =', chi2)
print('df =', df)
print('p =', 1-stats.chi2.cdf(chi2, df))

chi2 = 0
for p in ps:
    for i in range(q_control, total_q):
        expected = p.expected_scores[i]#sum(p.expected_scores[q_control:])
        observed = p.answers[i]#sum(p.answers[q_control:])
        chi2 += (observed - expected) ** 2 / expected

print('\nELO SCORE χ^2 STATISTICS (constantly updated, per question)')
print('χ^2 =', chi2)
print('df =', 3*(total_q-q_control)-1)
print('p =', 1-stats.chi2.cdf(chi2, 3*(total_q-q_control)-1))

chi2 = 0
for p in ps:
    expected = sum(p.expected_scores[q_control:])
    observed = sum(p.answers[q_control:])
    chi2 += (observed - expected) ** 2 / expected

print('\nELO SCORE χ^2 STATISTICS (constantly updated, for next 10 questions together)')
print('χ^2 =', chi2)
print('df =', df)
print('p =', 1-stats.chi2.cdf(chi2, df))

chi2 = 0
for p in ps:
    for answer in p.answers[q_control:]:
        expected = p.expected_scores[q_control]#*10
        observed = answer#sum(p.answers[q_control:])
        chi2 += (observed - expected) ** 2 / expected

print('\nELO SCORE χ^2 STATISTICS (at question 30, per question)')
print('χ^2 =', chi2)
print('df =', 3*(total_q-q_control)-1)
print('p =', 1-stats.chi2.cdf(chi2, 3*(total_q-q_control)-1))


chi2 = 0
for p in ps:
    expected = p.expected_scores[q_control]*10
    observed = sum(p.answers[q_control:])
    chi2 += (observed - expected) ** 2 / expected

print('\nELO SCORE χ^2 STATISTICS (at question 30, for next 10 questions together)')
print('χ^2 =', chi2)
print('df =', df)
print('p =', 1-stats.chi2.cdf(chi2, df))