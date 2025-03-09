#include<bits/stdc++.h>
#include<direct.h>
using namespace std;

int nowYear,nowMonth,nowDay;
fstream file;
string filePath = ".\\note.txt";
struct NoteItem {
    string subject, content;
};
bool compareSubjects(NoteItem noteA, NoteItem noteB) {
    return noteA.subject < noteB.subject;
}

int dateToDays(int year, int month, int day) {
    tm timeStruct = {};
    timeStruct.tm_year = year - 1900;
    timeStruct.tm_mon = month - 1;
    timeStruct.tm_mday = day;
    timeStruct.tm_hour = 0;
    timeStruct.tm_min = 0;
    timeStruct.tm_sec = 0;
    time_t time = mktime(&timeStruct);
    if (time == -1) {
        return -1;
    }
    return time / (60 * 60 * 24);
}
int dateDifference(int yearA, int monthA, int dayA, int yearB, int monthB, int dayB) {
    int dateA = dateToDays(yearA, monthA, dayA);
    int dateB = dateToDays(yearB, monthB, dayB);
    if (dateA == -1 || dateB == -1) return -1; // ������Ч����
    return dateB - dateA;
}
vector<string> splitByFourSpaces(const string& input) {
    vector<string> parts(5);
    vector<size_t> spacePositions;
    for (size_t i = 0; i < input.size() && spacePositions.size() < 4; ++i) {
        if (input[i] == ' ') spacePositions.push_back(i);
    }
    size_t lastPos = 0;
    for (int i = 0; i < 4; ++i) {
        if (i < spacePositions.size()) {
            parts[i] = input.substr(lastPos, spacePositions[i] - lastPos);
            lastPos = spacePositions[i] + 1;
        } else {
            parts[i] = "";
        }
    }
    if (spacePositions.size() >= 4) parts[4] = input.substr(lastPos);
    else  parts[4] = "";
    return parts;
}
vector<NoteItem> chooseNotes(int targetYear, int targetMonth, int targetDay, bool isFilter=true){
	vector<NoteItem> item;
	file.open(filePath, ios::in);
	if (!file.is_open()) {
	    cerr << ">>�޷����ļ�" << endl;
	    return item;
	}
	string line;
	while (getline(file, line)) {
	    auto a = splitByFourSpaces(line);
	    int difference = dateDifference(stoi(a[0]), stoi(a[1]), stoi(a[2]), targetYear, targetMonth, targetDay);
	    if (!isFilter || difference == 0 || difference == 1 || difference == 2 || difference == 4 || difference == 7 || difference == 15 || difference == 30 || difference == 60 || difference == 120 || difference == 240) {
	        item.push_back({a[3], a[4]});
	    }
	}
	file.close();
	return item;
}
void showItem(vector<NoteItem> item){
    sort(item.begin(), item.end(), compareSubjects);
    vector<NoteItem>::iterator t = item.begin();
    bool flag = false;
    string last="";
    for (; t != item.end(); t++) {
        if(last!=(*t).subject){
    		cout<< ">>" << (*t).subject<<endl;
    		last=(*t).subject;
		}
        cout << ">>  " << (*t).content << endl;
		flag = true;
    }
    if(!flag) cout << ">>�ޱ�������" << endl;
}
void exportNotesToMarkdown(const vector<NoteItem>& notes, string title, const string& path = "./answers/export.md") {
    if (notes.empty()) return;
    map<string, vector<string>> groupedNotes;
    for (const auto& note : notes) {
        groupedNotes[note.subject].push_back(note.content);
    }
    ofstream mdFile(path);
    mdFile << "## "<<title<<"\n\n";
    for (const auto& group : groupedNotes) {
        mdFile << "### [" << group.first << "](" << group.first << ")\n";
        for (const auto& content : group.second) {
            mdFile << "- [" << content << "](" << group.first<< "/" << content << ".md)\n";
        }
        mdFile << "\n";
    }
    mdFile.close();
}

int main() {
    cout << ">>1��д��" << endl << ">>2����ѯָ�����ڱ�������" << endl << ">>3����ѯ���б�������" << endl << ">>4���򿪴洢�ļ�" << endl << ">>0���˳�" << endl << endl;
    bool isFirstNoteInput = false;
    bool isFirstDateInput = false;
    system("git init");
	system("ssh -T git@github.com");
	while(true){
	    time_t now = time(0);
	    tm *localTime = localtime(&now);
	    nowYear = localTime->tm_year + 1900;
	    nowMonth = localTime->tm_mon + 1;
	    nowDay = localTime->tm_mday;
	    
        string dateString = to_string(nowYear)+"��"+to_string(nowMonth)+"��"+to_string(nowDay)+"��";
        auto item = chooseNotes(nowYear,nowMonth,nowDay);
    	exportNotesToMarkdown(item,dateString); 
	    
		system("git add . -f");
		system("git add ./answers/export.md -f");
		system("git branch -M main");
		system(("git commit -m \""+dateString+"\"").c_str());
		system("git push -f origin main");
    	
	    cout << "<<";
	    string n;
	    getline(cin, n);
	
	    if (n == "1") {
	        file.open(filePath, ios::app);
			if (!file.is_open()) {
			    cerr << ">>�޷����ļ�" << endl;
			    return -1;
			}
	        if(!isFirstNoteInput) cout << ">>�����룬�����ʽ����Ŀ(�ո�)���ݣ���Ŀ�����ݵ��о����ܰ����ո�ͻ��з�" << endl;
	        else cout << ">>������" << endl; 
			cout << "<<";
		    string item;
		    getline(cin, item);
	        file << nowYear << ' ' << nowMonth << ' ' << nowDay << ' ' << item << endl;
	        int index=item.find(" ");
			string subject=item.substr(0,index);
			string content=item.substr(index+1);
	        mkdir((".\\answers\\"+subject).c_str());
	        ofstream mdFile(".\\answers\\"+subject+"\\"+content+".md");
	        mdFile<<"## "<<content<<"\n\n";
	        isFirstNoteInput = true;
	        mdFile.close();
		    file.close();
	        system((".\\answers\\"+subject+"\\"+content+".md").c_str());
		    cout << ">>�����" << endl << endl;
	    }
	    else if (n == "2") {
	        if(!isFirstDateInput) cout << ">>���������ڣ������ʽ����(�ո�)��(�ո�)��" << endl << "<<";
	        else cout<< ">>������" << endl << "<<";
	        string date;
	        getline(cin,date);
	        auto d = splitByFourSpaces(date+" ");
	        auto item = chooseNotes(stoi(d[0]), stoi(d[1]), stoi(d[2]));
	    	showItem(item);
	    	isFirstDateInput=1;
		    cout << ">>�����" << endl << endl;
	    }
	    else if (n == "3") {
	        auto item = chooseNotes(nowYear,nowMonth,nowDay,false);
	    	showItem(item);
		    cout << ">>�����" << endl << endl;
	    }
	    else if (n == "4") {
	        cout << ">>�ȴ��У��رմ����Լ���" << endl;
	        system((filePath).c_str());
		    cout << ">>�����" << endl << endl;
	    }
	    else if (n == "0") {
		    cout << ">>���˳�" << endl << endl;
	        return 0;
	    }
	    else {
	        cout << ">>���ǿ��õ�����" << endl << endl;
	    }
	}
}

